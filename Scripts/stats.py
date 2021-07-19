import argparse
import yaml
import json
import os
from Scripts.TP_with_recovery import TokenPassingRecovery
import RoothPath
from Scripts.simulation import Simulation
from Scripts.simulation_new_recovery import SimulationNewRecovery
from statistics import *
import matplotlib.pyplot as plt

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
    tasks = param['tasks']
    delays = param['delays']

    # Simulate
    costs = []
    replans = []
    n_sim = 30
    k_list = [0, 1, 2, 3, 4, 5, 10]
    mean_costs_list = []
    mean_replans_list = []
    for k in k_list:
        for i in range(n_sim):
            #simulation = Simulation(tasks, agents, delays=delays)
            #tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=2000, k=k)
            simulation = SimulationNewRecovery(tasks, agents, delays=delays)
            tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000, k=k, new_recovery=True)
            while tp.get_completed_tasks() != len(tasks):
                simulation.time_forward(tp)
            cost = 0
            for path in simulation.actual_paths.values():
                cost = cost + len(path)
            costs.append(cost)
            replans.append(tp.get_n_replans())
        print('k:', k)
        print('Average cost:', mean(costs))
        print('Average number of replans:', mean(replans))
        mean_costs_list.append(mean(costs))
        mean_replans_list.append(mean(replans))
    plot1 = plt.figure(1)
    plt.plot(k_list, mean_costs_list, '-o')
    plot2 = plt.figure(2)
    plt.plot(k_list, mean_replans_list, '-o')
    plt.show()


