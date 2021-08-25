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
import time
import sys


def mute():
    sys.stdout = open(os.devnull, 'w')


def run_sim(param, n_sim, args, k_or_p_max):
    a_star_max_iter = args['a_star_max_iter']
    replan_every_k_delays = args['replan_every_k_delays']
    pd = args['pd']
    p_iter = args['p_iter']
    new_recovery = args['new_recovery']
    if pd is None:
        k = k_or_p_max
        p_max = None
    else:
        k = 0
        p_max = k_or_p_max

    costs = []
    replans = []
    sim_times = []
    dimensions = param['map']['dimensions']
    obstacles = param['map']['obstacles']
    non_task_endpoints = param['map']['non_task_endpoints']
    agents = param['agents']
    # Uncomment for fixed tasks and delays
    # tasks = param['tasks']
    # delays = param['delays']
    for i in range(n_sim):
        tasks, delays = gen_tasks_and_delays(agents, param['map']['start_locations'], param['map']['goal_locations'],
                                             param['n_tasks'],
                                             param['task_freq'], param['n_delays_per_agent'])
        # simulation = Simulation(tasks, agents, delays=delays)
        # tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=2000, k=k)
        simulation = SimulationNewRecovery(tasks, agents, delays=delays)
        # tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000,
        #                          k=k, new_recovery=True)
        tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation,
                                  a_star_max_iter=a_star_max_iter, k=k, replan_every_k_delays=replan_every_k_delays,
                                  pd=pd, p_max=p_max, p_iter=p_iter, new_recovery=new_recovery)
        start = time.time()
        while tp.get_completed_tasks() != len(tasks):
            simulation.time_forward(tp)
        cost = 0
        for path in simulation.actual_paths.values():
            cost = cost + len(path)
        costs.append(cost)
        replans.append(tp.get_n_replans())
        sim_times.append(time.time() - start)
    avg_cost = mean(costs)
    avg_n_replans = mean(replans)
    avg_computation_time_per_sim = mean(sim_times)
    print('k:', k)
    print('Average cost:', avg_cost)
    print('Average number of replans:', avg_n_replans)
    print('Average computation time per simulation:', avg_computation_time_per_sim)
    return [costs, replans, sim_times]

def run_sim_parall(param, args, k_or_p_max, n_single_sim):
    a_star_max_iter = args['a_star_max_iter']
    replan_every_k_delays = args['replan_every_k_delays']
    pd = args['pd']
    p_iter = args['p_iter']
    new_recovery = args['new_recovery']
    if pd is None:
        k = k_or_p_max
        p_max = None
    else:
        k = 0
        p_max = k_or_p_max

    dimensions = param['map']['dimensions']
    obstacles = param['map']['obstacles']
    non_task_endpoints = param['map']['non_task_endpoints']
    agents = param['agents']
    # Uncomment for fixed tasks and delays
    # tasks = param['tasks']
    # delays = param['delays']

    print('Simulation number:', n_single_sim)
    tasks, delays = gen_tasks_and_delays(agents, param['map']['start_locations'], param['map']['goal_locations'],
                                         param['n_tasks'],
                                         param['task_freq'], param['n_delays_per_agent'])
    # simulation = Simulation(tasks, agents, delays=delays)
    # tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=2000, k=k)
    simulation = SimulationNewRecovery(tasks, agents, delays=delays)
    # tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation, a_star_max_iter=1000,
    #                          k=k, new_recovery=True)
    tp = TokenPassingRecovery(agents, dimensions, obstacles, non_task_endpoints, simulation,
                              a_star_max_iter=a_star_max_iter, k=k, replan_every_k_delays=replan_every_k_delays,
                              pd=pd, p_max=p_max, p_iter=p_iter, new_recovery=new_recovery)
    start = time.time()
    while tp.get_completed_tasks() != len(tasks):
        simulation.time_forward(tp)
    cost = 0
    for path in simulation.actual_paths.values():
        cost = cost + len(path)

    return [cost, tp.get_n_replans(), time.time() - start]




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
    n_sim = 1
    args = {}
    args['a_star_max_iter'] = 20000
    args['replan_every_k_delays'] = False
    args['pd'] = 0.05
    args['p_iter'] = 1
    args['new_recovery'] = True
    #var_list = [0, 1, 2, 3, 4, 5]
    var_list = [1, 0.5, 0.25, 0.1, 0.05]
    costs_list = []
    replans_list = []
    sim_times_list = []
    start = time.time()
    pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
    compute_sim_partial = partial(run_sim, param, n_sim, args)
    resultList = pool.map(compute_sim_partial, var_list)
    pool.close()
    pool.join()
    for el in resultList:
        costs_list.append(el[0])
        replans_list.append(el[1])
        sim_times_list.append(el[2])
    print(time.time() - start)

    plot1 = plt.figure(1)
    plt.boxplot(costs_list, positions=var_list)
    plt.ylabel('Costs')
    plot2 = plt.figure(2)
    plt.boxplot(replans_list, positions=var_list)
    plt.ylabel('Number of replans')
    plot3 = plt.figure(3)
    plt.boxplot(sim_times_list, positions=var_list)
    plt.ylabel('Computation cost per simulation [s]')
    plt.show()



    costs_list = []
    replans_list = []
    sim_times_list = []
    start = time.time()
    for el in var_list:
        costs = []
        replans = []
        sim_times = []
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim_parall, param, args, el)
        resultList = pool.map(compute_sim_partial, range(n_sim))
        pool.close()
        pool.join()
        for el in resultList:
            costs.append(el[0])
            replans.append(el[1])
            sim_times.append(el[2])
        costs_list.append(costs)
        replans_list.append(replans)
        sim_times_list.append(sim_times)
    print(time.time() - start)

    plot1 = plt.figure(1)
    plt.boxplot(costs_list, positions=var_list)
    plt.ylabel('Costs')
    plot2 = plt.figure(2)
    plt.boxplot(replans_list, positions=var_list)
    plt.ylabel('Number of replans')
    plot3 = plt.figure(3)
    plt.boxplot(sim_times_list, positions=var_list)
    plt.ylabel('Computation cost per simulation [s]')
    plt.show()


