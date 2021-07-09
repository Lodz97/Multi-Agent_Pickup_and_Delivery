"""
Python implementation of Token Passing algorithms to solve MAPD problems with delays
author: Giacomo Lodigiani (@Lodz97)
"""
from math import fabs
import random
from Scripts.CBS.cbs import CBS, Environment


class TokenPassingRecovery(object):
    def __init__(self, agents, dimesions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000, k=1):
        self.agents = agents
        self.dimensions = dimesions
        self.obstacles = obstacles
        self.non_task_endpoints = non_task_endpoints
        if len(agents) > len(non_task_endpoints):
            print('There are more agents than non task endpoints, instance is not well-formed.')
            exit(1)
        # TODO: Check all properties for well-formedness
        self.token = {}
        self.simulation = simulation
        self.a_star_max_iter = a_star_max_iter
        self.k = k
        if k < 1:
            print('k should be >= 1!')
            exit(1)
        self.init_token()

    def init_token(self):
        self.token['agents'] = {}
        self.token['tasks'] = {}
        self.token['completed_tasks_times'] = {}
        for t in self.simulation.get_new_tasks():
            self.token['tasks'][t['task_name']] = [t['start'], t['goal']]
        self.token['agents_to_tasks'] = {}
        self.token['completed_tasks'] = 0
        self.token['path_ends'] = set()
        self.token['occupied_non_task_endpoints'] = set()
        self.token['delayed_agents'] = []
        self.token['delayed_agents_to_reach_task_start'] = []
        for a in self.agents:
            self.token['agents'][a['name']] = [a['start']]
            self.token['path_ends'].add(tuple(a['start']))

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

    def get_moving_obstacles_agents(self, agents_paths, time_start):
        obstacles = []
        for path in agents_paths:
            if len(path) > time_start and len(path) > 1:
                for i in range(time_start, len(path)):
                    k = i - time_start
                    obstacles.append((path[i][0], path[i][1], k))
                    for j in range(1, self.k + 1):
                        if i - j >= time_start:
                            obstacles.append((path[i][0], path[i][1], k - j))
                        obstacles.append((path[i][0], path[i][1], k + j))
                    # Mark last element with negative time to later turn it into idle obstacle
                    if i == len(path) - 1:
                        obstacles.append((path[i][0], path[i][1], -k))
        return obstacles

    def get_idle_obstacles_agents(self, agents_paths, time_start):
        obstacles = []
        for path in agents_paths:
            if len(path) == 1:
                obstacles.append((path[0][0], path[0][1]))
            if 1 < len(path) <= time_start:
                obstacles.append((path[-1][0], path[-1][1]))
        for agent_name in self.token['delayed_agents']:
            obstacles.append(tuple(self.token['agents'][agent_name][0]))
        return obstacles

    def check_safe_idle(self, agent_pos):
        for task_name, task in self.token['tasks'].items():
            if tuple(task[1]) == tuple(agent_pos):
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

    def get_completed_tasks(self):
        return self.token['completed_tasks']

    def get_completed_tasks_times(self):
        return self.token['completed_tasks_times']

    def get_token(self):
        return self.token

    def time_forward(self):
        # Update completed tasks
        for agent_name in self.token['agents']:
            pos = self.simulation.actual_paths[agent_name][-1]
            if agent_name in self.token['agents_to_tasks'] and (pos['x'], pos['y']) == tuple(self.token['agents_to_tasks'][agent_name]['goal']) \
            and len(self.token['agents'][agent_name]) == 1 and self.token['agents_to_tasks'][agent_name]['task_name'] != 'safe_idle':
                self.token['completed_tasks'] = self.token['completed_tasks'] + 1
                self.token['completed_tasks_times'][self.token['agents_to_tasks'][agent_name]['task_name']] = self.simulation.get_time()
                self.token['agents_to_tasks'].pop(agent_name)
            if agent_name in self.token['agents_to_tasks'] and (pos['x'], pos['y']) == tuple(self.token['agents_to_tasks'][agent_name]['goal']) \
            and len(self.token['agents'][agent_name]) == 1 and self.token['agents_to_tasks'][agent_name]['task_name'] == 'safe_idle':
                self.token['agents_to_tasks'].pop(agent_name)

        # Check delayed agents and agents affected by delays
        self.token['delayed_agents'] = []
        delayed_agents_pos = []
        for name, path in self.token['agents'].items():
            actual_state = self.simulation.get_actual_paths()[name][-1]
            if path[0] != [actual_state['x'], actual_state['y']]:
                print('Agent', name, 'delayed!')
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
                        self.update_ends(path[-1])
                        if path[0] in self.non_task_endpoints:
                            self.token['occupied_non_task_endpoints'].add(tuple(path[0]))
                        else:
                            self.token['path_ends'].add(tuple(path[0]))
                        if self.token['agents_to_tasks'][name]['start'] not in path:
                            self.token['delayed_agents_to_reach_task_start'].append(name)
                        self.token['agents'][name] = [path[0]]
                        break

        # Collect new tasks and assign them, if possible
        for t in self.simulation.get_new_tasks():
            self.token['tasks'][t['task_name']] = [t['start'], t['goal']]
        idle_agents = self.get_idle_agents()
        while len(idle_agents) > 0:
            agent_name = random.choice(list(idle_agents.keys()))
            # agent_name = list(idle_agents.keys())[0]
            all_idle_agents = self.token['agents'].copy()
            all_idle_agents.pop(agent_name)
            agent_pos = idle_agents.pop(agent_name)[0]
            available_tasks = {}
            for task_name, task in self.token['tasks'].items():
                if tuple(task[0]) not in self.token['path_ends'].difference({tuple(agent_pos)}) and tuple(task[1]) not in self.token['path_ends'].difference({tuple(agent_pos)}):
                    available_tasks[task_name] = task
            if len(available_tasks) > 0 or agent_name in self.token['agents_to_tasks']:
                if agent_name in self.token['agents_to_tasks']:
                    closest_task_name = self.token['agents_to_tasks'][agent_name]['task_name']
                    if agent_name in self.token['delayed_agents_to_reach_task_start']:
                        closest_task = [self.token['agents'][agent_name][0], self.token['agents_to_tasks'][agent_name]['goal']]
                    else:
                        closest_task = [self.token['agents_to_tasks'][agent_name]['start'], self.token['agents_to_tasks'][agent_name]['goal']]
                else:
                    closest_task_name = self.get_closest_task_name(available_tasks, agent_pos)
                    closest_task = available_tasks[closest_task_name]
                moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'].values(), 0)
                idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), 0)
                agent = {'name': agent_name, 'start': agent_pos, 'goal': closest_task[0]}
                env = Environment(self.dimensions, [agent], self.obstacles + idle_obstacles_agents, moving_obstacles_agents, a_star_max_iter=self.a_star_max_iter)
                cbs = CBS(env)
                path_to_task_start = cbs.search()
                if not path_to_task_start:
                    print("Solution not found to task start for agent", agent_name, " idling at current position...")
                    if len(self.token['delayed_agents']) == 0:
                        print('Instance is not well-formed or a_star_max_iter is too low for this environment.')
                        exit(1)
                else:
                    print("Solution found to task start for agent", agent_name, " searching solution to task goal...")
                    cost1 = env.compute_solution_cost(path_to_task_start)
                    # Use cost - 1 because idle cost is 1
                    moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'].values(), cost1-1)
                    idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), cost1-1)
                    agent = {'name': agent_name, 'start': closest_task[0], 'goal': closest_task[1]}
                    env = Environment(self.dimensions, [agent], self.obstacles + idle_obstacles_agents, moving_obstacles_agents, a_star_max_iter=self.a_star_max_iter)
                    cbs = CBS(env)
                    path_to_task_goal = cbs.search()
                    if not path_to_task_goal:
                        print("Solution not found to task goal for agent", agent_name, " idling at current position...")
                        if len(self.token['delayed_agents']) == 0:
                            print('Instance is not well-formed  or a_star_max_iter is too low for this environment.')
                            exit(1)
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
                        self.token['agents_to_tasks'][agent_name] = {'task_name': closest_task_name, 'start': task[0], 'goal': task[1], 'predicted_cost': cost1 + cost2}
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
                closest_non_task_endpoint = self.get_closest_non_task_endpoint(agent_pos)
                moving_obstacles_agents = self.get_moving_obstacles_agents(self.token['agents'].values(), 0)
                idle_obstacles_agents = self.get_idle_obstacles_agents(all_idle_agents.values(), 0)
                agent = {'name': agent_name, 'start': agent_pos, 'goal': closest_non_task_endpoint}
                env = Environment(self.dimensions, [agent], self.obstacles + idle_obstacles_agents, moving_obstacles_agents, a_star_max_iter=self.a_star_max_iter)
                cbs = CBS(env)
                path_to_non_task_endpoint = cbs.search()
                if not path_to_non_task_endpoint:
                    print("Solution to non-task endpoint not found for agent", agent_name, " instance is not well-formed.")
                    exit(1)
                else:
                    print('No available task for agent', agent_name, ' moving to safe idling position...')
                    self.update_ends(agent_pos)
                    self.token['occupied_non_task_endpoints'].add(tuple(closest_non_task_endpoint))
                    self.token['agents_to_tasks'][agent_name] = {'task_name': 'safe_idle', 'start': agent_pos,'goal': closest_non_task_endpoint, 'predicted_cost': 0}
                    self.token['agents'][agent_name] = []
                    for el in path_to_non_task_endpoint[agent_name]:
                        self.token['agents'][agent_name].append([el['x'], el['y']])

        # Advance along paths in the token
        for name, path in self.token['agents'].items():
            if len(path) > 1:
                self.token['agents'][name] = path[1:]


                        










