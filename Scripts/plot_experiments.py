import RoothPath
import json
import os
import matplotlib.pyplot as plt

with open(os.path.join(RoothPath.get_root(), 'all_experiments_25_08_2021_06_44_50.json'), 'r') as f:
    try:
        json_file = json.load(f)
    # If the file is empty the ValueError will be thrown
    except ValueError:
        json_file = {}

    i = 0
    for name, dic in json_file.items():
        plot1 = plt.figure(i + 1)
        plt.boxplot(dic['costs_list'], positions=dic['list'])
        plt.ylabel('Costs')
        plot2 = plt.figure(i + 2)
        plt.boxplot(dic['replans_list'], positions=dic['list'])
        plt.ylabel('Number of replans')
        plot3 = plt.figure(i + 3)
        plt.boxplot(dic['sim_times_list'], positions=dic['list'])
        plt.ylabel('Computation cost per simulation [s]')
        plt.show()
        i += 1