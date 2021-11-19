import RoothPath
import json
import numpy as np
import os
import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open(os.path.join(RoothPath.get_root(), 'config.json'), 'r') as json_file:
        config = json.load(json_file)

    file_name = config['experiments_file']

    with open(os.path.join(RoothPath.get_root(), config['experiments_path'], file_name), 'r') as f:
        try:
            json_file = json.load(f)
        # If the file is empty the ValueError will be thrown
        except ValueError:
            json_file = {}

        latex = False
        if latex:
            for name, dic in json_file.items():
                p_list = [1, 0.5, 0.25, 0.1, 0.05]
                #if 'crowded' not in name or 'freq=1' not in name:
                #continue
                print('#' * 10, name)
                c = [round(np.std(x), 2) for x in json_file[name.replace('_crowded', '')]['costs_list']][0:5] + [round(np.std(x), 2) for x in dic['costs_list']][0:5]
                r = [round(np.std(x), 2) for x in json_file[name.replace('_crowded', '')]['replans_list']][0:5] + [round(np.std(x), 2) for x in dic['replans_list']][0:5]
                s = [round(np.std(x), 2) for x in json_file[name.replace('_crowded', '')]['sim_times_list']][0:5] + [round(np.std(x), 2) for x in dic['sim_times_list']][0:5]
                for i in range(5):
                    if 'pd' not in name:
                        print('&', i, '&', c[i], '&', r[i], '&', s[i], '\\\\\cline{2-8}')
                    else:
                        print('&', p_list[i], '&', c[i], '&', r[i], '&', s[i], '\\\\\cline{2-8}')

        for name, dic in json_file.items():
            plt.subplot(1, 3, 1)
            plt.title(name)
            if dic['list'][0] == 0:
                plt.boxplot(dic['costs_list'], positions=dic['list'], showmeans=True)
                plt.xlabel('k')
            else:
                plt.boxplot(dic['costs_list'], showmeans=True)
                plt.xticks(range(1, len(dic['list']) + 1), dic['list'])
                plt.xlabel('p_threshold')
            plt.ylabel('Costs')
            plt.subplot(1, 3, 2)
            plt.title(name)
            if dic['list'][0] == 0:
                plt.boxplot(dic['replans_list'], positions=dic['list'], showmeans=True)
                plt.xlabel('k')
            else:
                plt.boxplot(dic['replans_list'], showmeans=True)
                plt.xticks(range(1, len(dic['list']) + 1), dic['list'])
                plt.xlabel('p_threshold')
            plt.ylabel('Number of replans')
            plt.subplot(1, 3, 3)
            plt.title(name)
            if dic['list'][0] == 0:
                plt.boxplot(dic['sim_times_list'], positions=dic['list'], showmeans=True)
                plt.xlabel('k')
            else:
                plt.boxplot(dic['sim_times_list'], showmeans=True)
                plt.xticks(range(1, len(dic['list']) + 1), dic['list'])
                plt.xlabel('p_threshold')
            plt.ylabel('Computation cost per simulation [s]')
            plt.show()

