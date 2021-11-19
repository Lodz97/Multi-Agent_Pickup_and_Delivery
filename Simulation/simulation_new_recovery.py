import argparse
import yaml
import json
import os
import time
from collections import defaultdict
from Simulation.TP_with_recovery import TokenPassingRecovery
import RoothPath
from Simulation.tasks_and_delays_maker import *


class SimulationNewRecovery(object):
    def __init__(self, tasks, agents, n_delays=0, delays=None):
        self.tasks = tasks
        self.agents = agents
        self.n_delays = n_delays
        self.delays = delays
        if self.delays is not None:
            self.n_delays = len(self.delays)
        self.time = 0
        self.start_times = []
        self.delay_times = []
        self.delayed_agents = set()
        self.agents_pos_now = set()
        self.agents_moved = set()
        self.actual_paths = {}
        self.times_agent_delayed = defaultdict(lambda: 0)
        self.delays_now = 0
        self.algo_time = 0
        self.initialize_simulation()

    def initialize_simulation(self):
        for t in self.tasks:
            self.start_times.append(t['start_time'])
        for agent in self.agents:
            self.actual_paths[agent['name']] = [{'t': 0, 'x': agent['start'][0], 'y': agent['start'][1]}]
        if self.delays is None:
            max_t = max(self.start_times)
            self.delay_times = random.choices(range(1, max_t + 10), k=self.n_delays)

    def increase_delay_counter(self, agent, k):
        self.times_agent_delayed[agent['name']] += 1
        if self.times_agent_delayed[agent['name']] == k:
            self.times_agent_delayed[agent['name']] = 0
            self.delayed_agents.add(agent['name'])

    def time_forward(self, algorithm):
        self.time = self.time + 1
        print('Time:', self.time)
        self.delays_now = self.delay_times.count(self.time)
        start_time = time.time()
        algorithm.time_forward()
        self.algo_time += time.time() - start_time
        self.delayed_agents = set()
        self.agents_pos_now = set()
        self.agents_moved = set()
        agents_to_move = self.agents
        random.shuffle(agents_to_move)
        # First "move" idle agents or agents stopped by delays
        for agent in agents_to_move:
            current_agent_pos = self.actual_paths[agent['name']][-1]
            self.agents_pos_now.add(tuple([current_agent_pos['x'], current_agent_pos['y']]))
            if len(algorithm.get_token()['agents'][agent['name']]) == 1:
                if algorithm.get_replan_every_k_delays():
                    self.times_agent_delayed[agent['name']] = 0
                self.agents_moved.add(agent['name'])
                self.actual_paths[agent['name']].append(
                    {'t': self.time, 'x': current_agent_pos['x'], 'y': current_agent_pos['y']})
            else:
                if self.delays is not None:
                    if self.time in self.delays[agent['name']]:
                        self.agents_moved.add(agent['name'])
                        if algorithm.get_replan_every_k_delays():
                            self.increase_delay_counter(agent, algorithm.get_k())
                        #self.delayed_agents.add(agent['name'])
                        # Don't consider forced replans
                        #algorithm.get_token()['n_replans'] = algorithm.get_token()['n_replans'] - 1
                        self.actual_paths[agent['name']].append(
                            {'t': self.time, 'x': current_agent_pos['x'], 'y': current_agent_pos['y']})
                elif self.delays_now > 0:
                    self.delays_now = self.delays_now - 1
                    self.agents_moved.add(agent['name'])
                    if algorithm.get_replan_every_k_delays():
                        self.increase_delay_counter(agent, algorithm.get_k())
                    #self.delayed_agents.add(agent['name'])
                    # Don't consider forced replans
                    #algorithm.get_token()['n_replans'] = algorithm.get_token()['n_replans'] - 1
                    self.actual_paths[agent['name']].append(
                        {'t': self.time, 'x': current_agent_pos['x'], 'y': current_agent_pos['y']})
        # Check moving agents doesn't collide with others
        agents_to_move = [x for x in agents_to_move if x['name'] not in self.agents_moved]
        moved_this_step = -1
        while moved_this_step != 0:
            moved_this_step = 0
            for agent in agents_to_move:
                current_agent_pos = self.actual_paths[agent['name']][-1]
                if agent['name'] not in self.delayed_agents:
                    if len(algorithm.get_token()['agents'][agent['name']]) > 1:
                        x_new = algorithm.get_token()['agents'][agent['name']][1][0]
                        y_new = algorithm.get_token()['agents'][agent['name']][1][1]
                        if tuple([x_new, y_new]) not in self.agents_pos_now or \
                                tuple([x_new, y_new]) == tuple(tuple([current_agent_pos['x'], current_agent_pos['y']])):
                            self.agents_moved.add(agent['name'])
                            self.agents_pos_now.remove(tuple([current_agent_pos['x'], current_agent_pos['y']]))
                            self.agents_pos_now.add(tuple([x_new, y_new]))
                            moved_this_step = moved_this_step + 1
                            algorithm.get_token()['agents'][agent['name']] = algorithm.get_token()['agents'][agent['name']][1:]
                            self.actual_paths[agent['name']].append({'t': self.time, 'x': x_new, 'y': y_new})
            agents_to_move = [x for x in agents_to_move if x['name'] not in self.agents_moved]
        for agent in agents_to_move:
            current_agent_pos = self.actual_paths[agent['name']][-1]
            if agent['name'] not in self.delayed_agents:
                self.delayed_agents.add(agent['name'])
                if algorithm.get_replan_every_k_delays():
                    self.times_agent_delayed[agent['name']] = 0
                self.agents_pos_now.add(tuple([current_agent_pos['x'], current_agent_pos['y']]))
                self.actual_paths[agent['name']].append(
                    {'t': self.time, 'x': current_agent_pos['x'], 'y': current_agent_pos['y']})

    def get_time(self):
        return self.time

    def get_algo_time(self):
        return self.algo_time

    def get_actual_paths(self):
        return self.actual_paths

    def get_new_tasks(self):
        new = []
        for t in self.tasks:
            if t['start_time'] == self.time:
                new.append(t)
        return new

    def get_delayed_agents(self):
        return self.delayed_agents


if __name__ == '__main__':
    random.seed(1234)
    parser = argparse.ArgumentParser()
    parser.add_argument('-param', help='Input file containing map and obstacles')
    parser.add_argument('-output', help='Output file with the schedule')
    args = parser.parse_args()

    if args.param is None:
        with open(os.path.join(RoothPath.get_root(), 'config.json'), 'r') as json_file:
            config = json.load(json_file)
        args.param = os.path.join(RoothPath.get_root(), os.path.join(config['input_path'], config['input_name']))
        args.output = os.path.join(RoothPath.get_root(), 'output.yaml')

    # Read from input file
    with open(args.param, 'r') as param_file:
        try:
            param = yaml.load(param_file, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    dimensions = param['map']['dimensions']
    obstacles = param['map']['obstacles']
    non_task_endpoints = param['map']['non_task_endpoints']
    agents = param['agents']
    # Old fixed tasks and delays
    #tasks = param['tasks']
    #delays = param['delays']
    # Generate random tasks and delays
    tasks, delays = gen_tasks_and_delays(agents, param['map']['start_locations'], param['map']['goal_locations'], param['n_tasks'], param['task_freq'], param['n_delays_per_agent'])
    param['tasks'] = tasks
    param['delays'] = delays
    with open(args.param + config['visual_postfix'], 'w') as param_file:
        yaml.safe_dump(param, param_file)

    # Simulate
    simulation = SimulationNewRecovery(tasks, agents, delays=delays)
    tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=4000, k=1,
                              replan_every_k_delays=False, pd=0.2, p_max=1, p_iter=1, new_recovery=True)
    while tp.get_completed_tasks() != len(tasks):
        simulation.time_forward(tp)

    cost = 0
    for path in simulation.actual_paths.values():
        cost = cost + len(path)
    output = {'schedule': simulation.actual_paths, 'cost': cost, 'completed_tasks_times': tp.get_completed_tasks_times(),
              'n_replans': tp.get_n_replans()}
    with open(args.output, 'w') as output_yaml:
        yaml.safe_dump(output, output_yaml)