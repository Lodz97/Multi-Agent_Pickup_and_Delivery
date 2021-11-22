"""
Python implementation of Token Passing algorithms to solve MAPD problems with delays
author: Giacomo Lodigiani (@Lodz97)
"""
from math import fabs
import random
from Simulation.CBS.cbs import CBS, Environment
from Simulation.markov_chains import MarkovChainsMaker
from collections import defaultdict


class TokenPassingRecovery(object):
    def __init__(self, agents, dimesions, obstacles, non_task_endpoints, simulation, a_star_max_iter=4000, k=0,
                 replan_every_k_delays=False, pd=None, p_max=1, p_iter=1, new_recovery=False):
        self.agents = agents
        self.dimensions = dimesions
        self.obstacles = set(obstacles)
        self.non_task_endpoints = non_task_endpoints
        if len(agents) > len(non_task_endpoints):
            print('There are more agents than non task endpoints, instance is not well-formed.')
            exit(1)
        # TODO: Check all properties for well-formedness
        self.token = {}
        self.simulation = simulation
        self.a_star_max_iter = a_star_max_iter
        self.k = k
        self.p_max = p_max
        if self.k != 0 and self.p_max != 1:
            print('Use of k and p robustness at same time not allowed.')
            exit(-1)
        if self.k < 0:
            print('k should be >= 0.')
            exit(1)
        if self.k == 0 and not new_recovery:
            print('k = 0 not supported for this recovery type.')
            exit(1)
        self.replan_every_k_delays = replan_every_k_delays
        if k == 0 and replan_every_k_delays:
            print('If k = 0 replan_every_k_delays must be False. Setting to False...')
            self.replan_every_k_delays = False
        if self.k == 0:
            if (self.p_max < 0 or self.p_max > 1):
                print('Max conflict probability must be between 0 and 1.')
                exit(1)
            self.pd = pd
            if self.p_max != 1 and not self.pd:
                print('To use p robustness need to set pd.')
                exit(1)
            if self.pd and (pd < 0 or pd > 1):
                print('Probability of delay must be between 0 and 1.')
                exit(1)
            self.p_iter = p_iter
            if self.p_iter <= 0:
                print('p_iter should be > 0.')
                exit(1)
        else:
            self.p_max = 1
            self.pd = None
            self.p_iter = 1
        self.new_recovery = new_recovery
        self.init_token()

    def init_token(self):
        self.token['agents'] = {}
        self.token['tasks'] = {}
        self.token['start_tasks_times'] = {}
        self.token['completed_tasks_times'] = {}
        for t in self.simulation.get_new_tasks():
            self.token['tasks'][t['task_name']] = [t['start'], t['goal']]
            self.token['start_tasks_times'][t['task_name']] = self.simulation.get_time()
        self.token['agents_to_tasks'] = {}
        self.token['completed_tasks'] = 0
        self.token['n_replans'] = 0
        self.token['path_ends'] = set()
        self.token['occupied_non_task_endpoints'] = set()
        self.token['delayed_agents'] = []
        self.token['delayed_agents_to_reach_task_start'] = []
        self.token['agent_at_end_path'] = []
        self.token['agent_at_end_path_pos'] = []
        self.token['agents_in_recovery_trial'] = []
        for a in self.agents:
            self.token['agents'][a['name']] = [a['start']]
            self.token['path_ends'].add(tuple(a['start']))
        self.token['prob_exceeded'] = False
        self.token['deadlock_count_per_agent'] = defaultdict(lambda: 0)

    def get_idle_agents(self):
        agents = {}
        for name, path in self.token['agents'].items():
            if len(path) == 1:
                agents[name] = path
        return agents

    def admissible_heuristic(self, task_pos, agent_pos):
        return fabs(task_pos[0] - agent_pos[0]) + fabs(task_pos[1] - agent_pos[1])

    def get_closest_task_name(self, available_tasks, agent_pos):
        closest = random.choice(list(available_tasks.keys()))
        dist = self.admissible_heuristic(available_tasks[closest][0], agent_pos)
        for task_name, task in available_tasks.items():
            if self.admissible_heuristic(task[0], agent_pos) < dist:
                closest = task_name
        return closest

    def get_moving_obstacles_agents(self, agents, time_start):
        obstacles = {}
        for name, path in agents.items():
            if len(path) > time_start and len(path) > 1:
                for i in range(time_start, len(path)):
                    k = i - time_start
                    obstacles[(path[i][0], path[i][1], k)] = name
                    for j in range(1, self.k + 1):
                        if i - j >= time_start:
                            obstacles[(path[i][0], path[i][1], k - j)] = name
                        obstacles[(path[i][0], path[i][1], k + j)] = name
                    # Mark last element with negative time to later turn it into idle obstacle
                    if i == len(path) - 1:
                        obstacles[(path[i][0], path[i][1], -k)] = name
        return obstacles

    def get_idle_obstacles_agents(self, agents_paths, delayed_agents, time_start):
        obstacles = set()
        for path in agents_paths:
            if len(path) == 1:
                obstacles.add((path[0][0], path[0][1]))
            if 1 < len(path) <= time_start:
                obstacles.add((path[-1][0], path[-1][1]))
        for agent_name in delayed_agents:
            obstacles.add(tuple(self.token['agents'][agent_name][0]))
        return obstacles

    def check_safe_idle(self, agent_pos):
        for task_name, task in self.token['tasks'].items():
            if tuple(task[0]) == tuple(agent_pos) or tuple(task[1]) == tuple(agent_pos):
                return False
        for start_goal in self.get_agents_to_tasks_starts_goals():
            if tuple(start_goal) == tuple(agent_pos):
                return False
        return True

    def get_closest_non_task_endpoint(self, agent_pos):
        dist = -1
        res = -1
        for endpoint in self.non_task_endpoints:
            if endpoint not in self.token['occupied_non_task_endpoints']:
                if dist == -1:
                    dist = self.admissible_heuristic(endpoint, agent_pos)
                    res = endpoint
                else:
                    tmp = self.admissible_heuristic(endpoint, agent_pos)
                    if tmp < dist:
                        dist = tmp
                        res = endpoint
        if res == -1:
            print('Error in finding non-task endpoint, is instance well-formed?')
            exit(1)
        return res

    def update_ends(self, agent_pos):
        if tuple(agent_pos) in self.token['path_ends']:
            self.token['path_ends'].remove(tuple(agent_pos))
        elif tuple(agent_pos) in self.token['occupied_non_task_endpoints']:
            self.token['occupied_non_task_endpoints'].remove(tuple(agent_pos))

    def get_agents_to_tasks_goals(self):
        goals = set()
        for el in self.token['agents_to_tasks'].values():
            goals.add(tuple(el['goal']))
        return goals

    def get_agents_to_tasks_starts_goals(self):
        starts_goals = set()
        for el in self.token['agents_to_tasks'].values():
            starts_goals.add(tuple(el['goal']))
            starts_goals.add(tuple(el['start']))
        return starts_goals

    def get_completed_tasks(self):
        return self.token['completed_tasks']

    def get_completed_tasks_times(self):
        return self.token['completed_tasks_times']

    def get_n_replans(self):
        return self.token['n_replans']

    def get_token(self):
        return self.token

    def get_k(self):
        return self.k

    def get_replan_every_k_delays(self):
        return self.replan_every_k_delays

    def search(self, cbs, agent_name, moving_obstacles_agents):
        path = None
        if self.p_max == 1:
            path = cbs.search()
        else:
            self.token['prob_exceeded'] = False
            mk = MarkovChainsMaker(self.token['agents'], self.pd)
            for iter in range(self.p_iter):
                path = cbs.search()
                tmp = []
                if path and len(path[agent_name]) > 1:
                    for el in path[agent_name]:
                        tmp.append([el['x'], el['y']])
                    dic = mk.get_conflict_prob_given_path(tmp)
                    if dic['prob'] > self.p_max:
                        self.token['prob_exceeded'] = True
                        print('Conflict probablility to high (', dic['prob'], ') replanning...')
                        path = None
                        moving_obstacles_agents[(dic['pos_max_conf'][0], dic['pos_max_conf'][1], -1)] = agent_name
                    else:
                        break
        return path

    def go_to_closest_non_task_endpoint(self, agent_name, agent_pos, all_idle_agents, all_delayed_agents):
        closest_non_task_endpoint = self.get_closest_non_task_endpoint(agent_pos)
        moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'], 0)
        idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), all_delayed_agents, 0)
        agent = {'name': agent_name, 'start': agent_pos, 'goal': closest_non_task_endpoint}
        env = Environment(self.dimensions, [agent], self.obstacles | idle_obstacles_agents, moving_obstacles_agents,
                          a_star_max_iter=self.a_star_max_iter)
        cbs = CBS(env)
        path_to_non_task_endpoint = self.search(cbs, agent_name, moving_obstacles_agents)
        if not path_to_non_task_endpoint:
            print("Solution to non-task endpoint not found for agent", agent_name, " instance is not well-formed.")
            self.deadlock_recovery(agent_name, agent_pos, all_idle_agents, all_delayed_agents, 4)
            # exit(1)
        else:
            print('No available task for agent', agent_name, ' moving to safe idling position...')
            self.update_ends(agent_pos)
            self.token['occupied_non_task_endpoints'].add(tuple(closest_non_task_endpoint))
            self.token['agents_to_tasks'][agent_name] = {'task_name': 'safe_idle', 'start': agent_pos,
                                                         'goal': closest_non_task_endpoint, 'predicted_cost': 0}
            self.token['agents'][agent_name] = []
            for el in path_to_non_task_endpoint[agent_name]:
                self.token['agents'][agent_name].append([el['x'], el['y']])

    def get_random_close_cell(self, agent_pos, r):
        while True:
            cell = (agent_pos[0] + random.choice(range(-r - 1, r + 1)), agent_pos[1] + random.choice(range(-r - 1, r + 1)))
            if cell not in self.obstacles and cell not in self.token['path_ends'] and \
                    cell not in self.token['occupied_non_task_endpoints'] \
                    and cell not in self.get_agents_to_tasks_goals() \
                    and 0 <= cell[0] < self.dimensions[0] and 0 <= cell[1] < self.dimensions[1]:
                return cell

    def deadlock_recovery(self, agent_name, agent_pos, all_idle_agents, all_delayed_agents, r):
        self.token['deadlock_count_per_agent'][agent_name] += 1
        if self.token['deadlock_count_per_agent'][agent_name] >= 5:
            self.token['deadlock_count_per_agent'][agent_name] = 0
            random_close_cell = self.get_random_close_cell(agent_pos, r)
            moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'], 0)
            idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), all_delayed_agents, 0)
            agent = {'name': agent_name, 'start': agent_pos, 'goal': random_close_cell}
            env = Environment(self.dimensions, [agent], self.obstacles | idle_obstacles_agents, moving_obstacles_agents,
                              a_star_max_iter=self.a_star_max_iter)
            cbs = CBS(env)
            path_to_non_task_endpoint = self.search(cbs, agent_name, moving_obstacles_agents)
            if not path_to_non_task_endpoint:
                print("No solution to deadlock recovery for agent", agent_name, " retrying later.")
            else:
                # Don't consider this a task, so don't add to agents_to_tasks
                print('Agent', agent_name, 'causing deadlock, moving to safer position...')
                self.update_ends(agent_pos)
                self.token['agents'][agent_name] = []
                for el in path_to_non_task_endpoint[agent_name]:
                    self.token['agents'][agent_name].append([el['x'], el['y']])

    def time_forward(self):
        # Update completed tasks
        for agent_name in self.token['agents']:
            pos = self.simulation.actual_paths[agent_name][-1]
            if agent_name in self.token['agents_to_tasks'] and (pos['x'], pos['y']) == tuple(
                    self.token['agents_to_tasks'][agent_name]['goal']) \
                    and len(self.token['agents'][agent_name]) == 1 and self.token['agents_to_tasks'][agent_name][
                'task_name'] != 'safe_idle':
                self.token['completed_tasks'] = self.token['completed_tasks'] + 1
                self.token['completed_tasks_times'][
                    self.token['agents_to_tasks'][agent_name]['task_name']] = self.simulation.get_time()
                self.token['agents_to_tasks'].pop(agent_name)
            if agent_name in self.token['agents_to_tasks'] and (pos['x'], pos['y']) == tuple(
                    self.token['agents_to_tasks'][agent_name]['goal']) \
                    and len(self.token['agents'][agent_name]) == 1 and self.token['agents_to_tasks'][agent_name][
                'task_name'] == 'safe_idle':
                self.token['agents_to_tasks'].pop(agent_name)

        # Check delayed agents and agents affected by delays
        if self.new_recovery:
            self.token['delayed_agents'] = self.simulation.get_delayed_agents()
            for name in self.token['delayed_agents']:
                print('Agent', name, 'delayed or affected by delay!')
                path = self.token['agents'][name]
                self.token['n_replans'] = self.token['n_replans'] + 1
                self.update_ends(path[-1])
                if path[0] in self.non_task_endpoints:
                    self.token['occupied_non_task_endpoints'].add(tuple(path[0]))
                else:
                    self.token['path_ends'].add(tuple(path[0]))
                if name in self.token['agents_to_tasks']:
                    if self.token['agents_to_tasks'][name]['start'] not in path:
                        self.token['delayed_agents_to_reach_task_start'].append(name)
                self.token['agents'][name] = [path[0]]
        else:
            self.token['delayed_agents'] = []
            delayed_agents_pos = []
            for name, path in self.token['agents'].items():
                actual_state = self.simulation.get_actual_paths()[name][-1]
                if path[0] != [actual_state['x'], actual_state['y']]:
                    print('Agent', name, 'delayed!')
                    # self.token['n_replans'] = self.token['n_replans'] + 1
                    self.token['delayed_agents'].append(name)
                    delayed_agents_pos.append([actual_state['x'], actual_state['y']])
                    self.update_ends(path[-1])
                    pos = tuple([actual_state['x'], actual_state['y']])
                    if pos in self.non_task_endpoints:
                        self.token['occupied_non_task_endpoints'].add(pos)
                    else:
                        self.token['path_ends'].add(pos)
                    if self.token['agents_to_tasks'][name]['start'] not in path:
                        self.token['delayed_agents_to_reach_task_start'].append(name)
                    self.token['agents'][name] = [[actual_state['x'], actual_state['y']]]
            for name, path in self.token['agents'].items():
                if name not in self.token['delayed_agents']:
                    for i in range(len(path)):
                        if path[i] in delayed_agents_pos:
                            print('Agent', name, 'affected by delay!')
                            self.token['n_replans'] = self.token['n_replans'] + 1
                            self.update_ends(path[-1])
                            if path[0] in self.non_task_endpoints:
                                self.token['occupied_non_task_endpoints'].add(tuple(path[0]))
                            else:
                                self.token['path_ends'].add(tuple(path[0]))
                            if self.token['agents_to_tasks'][name]['start'] not in path:
                                self.token['delayed_agents_to_reach_task_start'].append(name)
                            self.token['agents'][name] = [path[0]]
                            break

        # TODO do this maybe only for old recovery
        # Check if somehow an agent path collides with an idle agent (may happen because of delays)
        if not self.new_recovery:
            for name, path in self.get_idle_agents().items():
                self.token['agent_at_end_path'].append(name)
                self.token['agent_at_end_path_pos'].append(path[0])
            for name, path in self.token['agents'].items():
                if name not in self.token['agent_at_end_path']:
                    for i in range(len(path)):
                        if path[i] in self.token['agent_at_end_path_pos']:
                            print('Agent', name, 'will impact end task agent, replanning...')
                            # self.update_ends(path[-1])
                            if path[0] in self.non_task_endpoints:
                                self.token['occupied_non_task_endpoints'].add(tuple(path[0]))
                            else:
                                self.token['path_ends'].add(tuple(path[0]))
                            # TODO check this rare keyerror
                            if self.token['agents_to_tasks'][name]['start'] not in path:
                                self.token['delayed_agents_to_reach_task_start'].append(name)
                            self.token['agents'][name] = [path[0]]
                            break
            self.token['agent_at_end_path'] = []
            self.token['agent_at_end_path_pos'] = []

        # Collect new tasks and assign them, if possible
        for t in self.simulation.get_new_tasks():
            self.token['tasks'][t['task_name']] = [t['start'], t['goal']]
            self.token['start_tasks_times'][t['task_name']] = self.simulation.get_time()
        idle_agents = self.get_idle_agents()
        while len(idle_agents) > 0:
            agent_name = random.choice(list(idle_agents.keys()))
            # agent_name = list(idle_agents.keys())[0]
            all_idle_agents = self.token['agents'].copy()
            all_idle_agents.pop(agent_name)
            all_delayed_agents = self.token['delayed_agents'].copy()
            if agent_name in all_delayed_agents:
                all_delayed_agents.remove(agent_name)
            agent_pos = idle_agents.pop(agent_name)[0]
            available_tasks = {}
            for task_name, task in self.token['tasks'].items():
                if tuple(task[0]) not in self.token['path_ends'].difference({tuple(agent_pos)}) and tuple(
                        task[1]) not in self.token['path_ends'].difference({tuple(agent_pos)}) \
                        and tuple(task[0]) not in self.get_agents_to_tasks_goals() and tuple(
                    task[1]) not in self.get_agents_to_tasks_goals():
                    available_tasks[task_name] = task
            if len(available_tasks) > 0 or agent_name in self.token['agents_to_tasks']:
                if agent_name in self.token['agents_to_tasks']:
                    closest_task_name = self.token['agents_to_tasks'][agent_name]['task_name']
                    if agent_name in self.token['delayed_agents_to_reach_task_start']:
                        closest_task = [self.token['agents'][agent_name][0],
                                        self.token['agents_to_tasks'][agent_name]['goal']]
                    else:
                        closest_task = [self.token['agents_to_tasks'][agent_name]['start'],
                                        self.token['agents_to_tasks'][agent_name]['goal']]
                else:
                    closest_task_name = self.get_closest_task_name(available_tasks, agent_pos)
                    closest_task = available_tasks[closest_task_name]
                moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'], 0)
                idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), all_delayed_agents, 0)
                agent = {'name': agent_name, 'start': agent_pos, 'goal': closest_task[0]}
                env = Environment(self.dimensions, [agent], self.obstacles | idle_obstacles_agents,
                                  moving_obstacles_agents, a_star_max_iter=self.a_star_max_iter)
                cbs = CBS(env)
                path_to_task_start = self.search(cbs, agent_name, moving_obstacles_agents)
                if not path_to_task_start:
                    print("Solution not found to task start for agent", agent_name, " idling at current position...")
                    if len(self.token['delayed_agents']) == 0 and not self.token['prob_exceeded']:
                        print('Instance is not well-formed or a_star_max_iter is too low for this environment.')
                        self.deadlock_recovery(agent_name, agent_pos, all_idle_agents, all_delayed_agents, 4)
                        # exit(1)
                else:
                    print("Solution found to task start for agent", agent_name, " searching solution to task goal...")
                    cost1 = env.compute_solution_cost(path_to_task_start)
                    # Use cost - 1 because idle cost is 1
                    moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'], cost1 - 1)
                    idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), all_delayed_agents,
                                                                           cost1 - 1)
                    agent = {'name': agent_name, 'start': closest_task[0], 'goal': closest_task[1]}
                    env = Environment(self.dimensions, [agent], self.obstacles | idle_obstacles_agents,
                                      moving_obstacles_agents, a_star_max_iter=self.a_star_max_iter)
                    cbs = CBS(env)
                    path_to_task_goal = self.search(cbs, agent_name, moving_obstacles_agents)
                    if not path_to_task_goal:
                        print("Solution not found to task goal for agent", agent_name, " idling at current position...")
                        if len(self.token['delayed_agents']) == 0 and not self.token['prob_exceeded']:
                            print('Instance is not well-formed  or a_star_max_iter is too low for this environment.')
                            self.deadlock_recovery(agent_name, agent_pos, all_idle_agents, all_delayed_agents, 4)
                            # exit(1)
                    else:
                        print("Solution found to task goal for agent", agent_name, " doing task...")
                        cost2 = env.compute_solution_cost(path_to_task_goal)
                        if agent_name not in self.token['agents_to_tasks']:
                            self.token['tasks'].pop(closest_task_name)
                            task = available_tasks.pop(closest_task_name)
                        else:
                            task = closest_task
                        if agent_name in self.token['delayed_agents_to_reach_task_start']:
                            self.token['delayed_agents_to_reach_task_start'].remove(agent_name)
                        last_step = path_to_task_goal[agent_name][-1]
                        self.update_ends(agent_pos)
                        self.token['path_ends'].add(tuple([last_step['x'], last_step['y']]))
                        self.token['agents_to_tasks'][agent_name] = {'task_name': closest_task_name, 'start': task[0],
                                                                     'goal': task[1], 'predicted_cost': cost1 + cost2}
                        self.token['agents'][agent_name] = []
                        for el in path_to_task_start[agent_name]:
                            self.token['agents'][agent_name].append([el['x'], el['y']])
                        # Don't repeat twice same step
                        self.token['agents'][agent_name] = self.token['agents'][agent_name][:-1]
                        for el in path_to_task_goal[agent_name]:
                            self.token['agents'][agent_name].append([el['x'], el['y']])
            elif self.check_safe_idle(agent_pos):
                print('No available tasks for agent', agent_name, ' idling at current position...')
            else:
                self.go_to_closest_non_task_endpoint(agent_name, agent_pos, all_idle_agents, all_delayed_agents)

        # Advance along paths in the token
        if not self.new_recovery:
            for name, path in self.token['agents'].items():
                if len(path) > 1:
                    self.token['agents'][name] = path[1:]
