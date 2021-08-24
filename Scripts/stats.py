import argparse
import yaml
import json
import os
from Scripts.TP_with_recovery import TokenPassingRecovery
import RoothPath
from Scripts.simulation import Simulation
from Scripts.simulation_new_recovery import SimulationNewRecovery
from Scripts.tasks_and_delays_maker import *
from statistics import *
import matplotlib.pyplot as plt
from Utils.pool_with_subprocess import PoolWithSubprocess
import multiprocessing
from functools import partial


def run_sim(param, n_sim, k):
    costs = []
    replans = []
    dimensions = param['map']['dimensions']
    obstacles = param['map']['obstacles']
    non_task_endpoints = param['map']['non_task_endpoints']
    agents = param['agents']
    # Uncomment for fixed tasks and delays
    #tasks = param['tasks']
    #delays = param['delays']
    for i in range(n_sim):
        tasks, delays = gen_tasks_and_delays(agents, param['start_locations'], param['goal_locations'],
                                             param['n_tasks'],
                                             param['task_freq'], param['n_delays_per_agent'])
        # simulation = Simulation(tasks, agents, delays=delays)
        # tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=2000, k=k)
        simulation = SimulationNewRecovery(tasks, agents, delays=delays)
        tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000,
                                  k=k, new_recovery=True)
        # tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation,
        #                          a_star_max_iter=1000, k=0, p_max=k, pd=0.1, p_iter=5, new_recovery=True)
        while tp.get_completed_tasks() != len(tasks):
            simulation.time_forward(tp)
        cost = 0
        for path in simulation.actual_paths.values():
            cost = cost + len(path)
        costs.append(cost)
        replans.append(tp.get_n_replans())
    avg_cost = mean(costs)
    avg_n_replans = mean(replans)
    print('k:', k)
    print('Average cost:', avg_cost)
    print('Average number of replans:', avg_n_replans)
    return [costs, replans]


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

    # Simulate
    n_sim = 100
    k_list = [0, 1, 2, 3]
    #k_list = [1, 0.5, 0.3, 0.2, 0.1, 0.02]
    costs_list = []
    replans_list = []
    pool = PoolWithSubprocess(processes=multiprocessing.cpu_count() // 2, maxtasksperchild=1)
    compute_sim_partial = partial(run_sim, param, n_sim)
    resultList = pool.map(compute_sim_partial, k_list)
    pool.close()
    pool.join()
    for el in resultList:
        costs_list.append(el[0])
        replans_list.append(el[1])
    plot1 = plt.figure(1)
    plt.boxplot(costs_list, positions=k_list)
    plot2 = plt.figure(2)
    plt.boxplot(replans_list, positions=k_list)
    plt.show()


