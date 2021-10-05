import os
import RoothPath
import yaml
import json
import random
from Scripts.stats import run_sim
from Utils.pool_with_subprocess import PoolWithSubprocess
import multiprocessing
from functools import partial
from datetime import datetime


if __name__ == '__main__':
    with open(os.path.join(RoothPath.get_root(), 'config.json'), 'r') as json_file:
        config = json.load(json_file)
    env_folder = os.path.join(RoothPath.get_root(), os.path.join(config['input_path']))
    output = 'experiments_new_' + datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + '.json'
    with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
        json.dump({}, f)
    random.seed(1234)

    for freq in [0.5, 1, 3]:
        #####################################
        # Read from input file
        # 1
        random.seed(1234)
        name = 'input_warehouse_small_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_small_k_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = None
        args['p_iter'] = 5
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [0, 1, 2, 3, 4, 5]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        ####################################
        # Read from input file
        # 2
        random.seed(1234)
        name = 'input_warehouse_small_crowded_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_small_crowded_k_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = None
        args['p_iter'] = 5
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [0, 1, 2, 3, 4, 5]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        ####################################
        # Read from input file
        # 3
        random.seed(1234)
        name = 'input_warehouse_mid_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_mid_k_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = None
        args['p_iter'] = 5
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [0, 1, 2, 3, 4, 5]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        ####################################
        # Read from input file
        # 4
        random.seed(1234)
        name = 'input_warehouse_mid_crowded_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_mid_crowded_k_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = None
        args['p_iter'] = 5
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [0, 1, 2, 3, 4]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 5
        random.seed(1234)
        name = 'input_warehouse_small_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_small_pd=0.1_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.1
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 6
        random.seed(1234)
        name = 'input_warehouse_small_crowded_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_small_crowded_pd=0.1_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.1
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 7
        random.seed(1234)
        name = 'input_warehouse_mid_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_mid_pd=0.1_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.1
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 8
        random.seed(1234)
        name = 'input_warehouse_mid_crowded_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_mid_crowded_pd=0.1_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.1
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 9
        random.seed(1234)
        name = 'input_warehouse_small_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_small_pd=0.02_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.02
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 10
        random.seed(1234)
        name = 'input_warehouse_small_crowded_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_small_crowded_pd=0.02_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.02
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 11
        random.seed(1234)
        name = 'input_warehouse_mid_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_mid_pd=0.02_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.02
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

        #####################################
        # Read from input file
        # 12
        random.seed(1234)
        name = 'input_warehouse_mid_crowded_random.yaml'
        input = os.path.join(env_folder, name)
        with open(input, 'r') as param_file:
            try:
                param = yaml.load(param_file, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        # Simulate
        n_sim = 100
        with open(os.path.join(RoothPath.get_root(), output), 'r') as f:
            try:
                json_file = json.load(f)
            # If the file is empty the ValueError will be thrown
            except ValueError:
                json_file = {}
        args = {}
        json_file['warehouse_mid_crowded_pd=0.02_freq=' + str(freq)] = args
        args['n_sim'] = n_sim
        args['a_star_max_iter'] = 4000
        args['replan_every_k_delays'] = False
        args['pd'] = 0.02
        args['p_iter'] = 1
        args['new_recovery'] = True
        args['n_tasks'] = param['n_tasks']
        args['task_freq'] = freq
        args['n_delays_per_agent'] = param['n_delays_per_agent']
        var_list = [1, 0.5, 0.25, 0.1, 0.05]
        args['list'] = var_list
        costs_list = []
        replans_list = []
        sim_times_list = []
        args['costs_list'] = costs_list
        args['replans_list'] = replans_list
        args['sim_times_list'] = sim_times_list
        pool = PoolWithSubprocess(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
        compute_sim_partial = partial(run_sim, param, n_sim, args)
        resultList = pool.map(compute_sim_partial, var_list)
        pool.close()
        pool.join()
        for el in resultList:
            costs_list.append(el[0])
            replans_list.append(el[1])
            sim_times_list.append(el[2])
        with open(os.path.join(RoothPath.get_root(), output), 'w') as f:
            json.dump(json_file, f)

