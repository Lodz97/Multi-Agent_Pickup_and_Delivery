import argparse
from collections import defaultdict
import yaml
import json
import os
from Scripts.TP_with_recovery import TokenPassingRecovery
import RoothPath
from Scripts.simulation import Simulation
from Scripts.simulation_new_recovery import SimulationNewRecovery
from Scripts.tasks_and_delays_maker import *
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-param', help='Input file containing map and obstacles')
    parser.add_argument('-output', help='Output file with the schedule')
    args = parser.parse_args()

    if args.param is None:
        with open(os.path.join(RoothPath.get_root(), 'config.json'), 'r') as json_file:
            config = json.load(json_file)
        args.param = os.path.join(RoothPath.get_root(), os.path.join(config['input_path'], config['input_name']))
        args.output = 'output.yaml'

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
    #tasks = param['tasks']
    #delays = param['delays']

    # Simulate
    n_sim = 100
    states_dict = defaultdict(lambda: 0)
    n_conflicts = 0
    start_time = time.time()
    for k in [0]:
        for i in range(n_sim):
            tasks, delays = gen_tasks_and_delays(agents, param['start_locations'], param['goal_locations'],
                                                 param['n_tasks'],
                                                 param['task_freq'], param['n_delays_per_agent'])
            param['tasks'] = tasks
            param['delays'] = delays
            with open(args.param + config['visual_postfix'], 'w') as param_file:
                yaml.safe_dump(param, param_file)
            #simulation = Simulation(tasks, agents, delays=delays)
            #tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000, k=k)
            simulation = SimulationNewRecovery(tasks, agents, delays=delays)
            tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000, k=k, new_recovery=True)
            while tp.get_completed_tasks() != len(tasks):
                simulation.time_forward(tp)
            for path in simulation.actual_paths.values():
                for step in path:
                    states_dict[str(step['t']) + '_' + str(step['x']) + '_' + str(step['y'])] = states_dict[str(step['t']) + '_' + str(step['x']) + '_' + str(step['y'])] + 1
            for el in states_dict.values():
                if el > 1:
                    n_conflicts = n_conflicts + 1
                    cost = 0
                    for path in simulation.actual_paths.values():
                        cost = cost + len(path)
                    output = {'schedule': simulation.actual_paths, 'cost': cost,
                              'completed_tasks_times': tp.get_completed_tasks_times()}
                    with open(args.output, 'w') as output_yaml:
                        yaml.safe_dump(output, output_yaml)
            states_dict = defaultdict(lambda: 0)
            if n_conflicts > 0:
                break
        print('k:', k)
        print('Conflicts:', n_conflicts)
        print('Average time per simulation:', (time.time() - start_time) / 100)
