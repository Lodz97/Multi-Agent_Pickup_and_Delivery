import RoothPath
import json
import os
import matplotlib.pyplot as plt

with open(os.path.join(RoothPath.get_root(), 'all_experiments_26_08_2021.json'), 'r') as f:
    try:
        json_file = json.load(f)
    # If the file is empty the ValueError will be thrown
    except ValueError:
        json_file = {}

    for name, dic in json_file.items():
        plt.subplot(1, 3, 1)
        plt.title(name)
        if dic['list'][0] == 0:
            plt.boxplot(dic['costs_list'], positions=dic['list'])
            plt.xlabel('k')
        else:
            plt.boxplot(dic['costs_list'])
            plt.xticks(range(1, len(dic['list']) + 1), dic['list'])
            plt.xlabel('p_max')
        plt.ylabel('Costs')
        plt.subplot(1, 3, 2)
        plt.title(name)
        if dic['list'][0] == 0:
            plt.boxplot(dic['replans_list'], positions=dic['list'])
            plt.xlabel('k')
        else:
            plt.boxplot(dic['replans_list'])
            plt.xticks(range(1, len(dic['list']) + 1), dic['list'])
            plt.xlabel('p_max')
        plt.ylabel('Number of replans')
        plt.subplot(1, 3, 3)
        plt.title(name)
        if dic['list'][0] == 0:
            plt.boxplot(dic['sim_times_list'], positions=dic['list'])
            plt.xlabel('k')
        else:
            plt.boxplot(dic['sim_times_list'])
            plt.xticks(range(1, len(dic['list']) + 1), dic['list'])
            plt.xlabel('p_max')
        plt.ylabel('Computation cost per simulation [s]')
        plt.show()

