#!/usr/bin/env python3
import yaml
import matplotlib
# matplotlib.use("Agg")
from matplotlib.patches import Circle, Rectangle, Arrow, RegularPolygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import matplotlib.animation as manimation
import argparse
import math
import json
import os
import RoothPath


Colors = ['orange', 'blue', 'green']


class Animation:
    def __init__(self, map, schedule, slow_factor=10):
        self.map = map
        self.schedule = schedule
        self.slow_factor = slow_factor
        self.combined_schedule = {}
        self.combined_schedule.update(self.schedule["schedule"])

        aspect = map["map"]["dimensions"][0] / map["map"]["dimensions"][1]

        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=None, hspace=None)
        # self.ax.set_frame_on(False)

        self.patches = []
        self.artists = []
        self.agents = dict()
        self.agent_names = dict()
        self.tasks = dict()
        # Create boundary patch
        xmin = -0.5
        ymin = -0.5
        xmax = map["map"]["dimensions"][0] - 0.5
        ymax = map["map"]["dimensions"][1] - 0.5

        # self.ax.relim()
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
        # self.ax.set_xticks([])
        # self.ax.set_yticks([])
        # plt.axis('off')
        # self.ax.axis('tight')
        # self.ax.axis('off')

        self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
        for x in range(map["map"]["dimensions"][0]):
            for y in range(map["map"]["dimensions"][1]):
                self.patches.append(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='black'))
        for o in map["map"]["obstacles"]:
            x, y = o[0], o[1]
            self.patches.append(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='black', edgecolor='black'))
        for e in map["map"]["non_task_endpoints"]:
            x, y = e[0], e[1]
            self.patches.append(Circle((x, y), 0.4, facecolor='green', edgecolor='black'))

        task_colors = np.random.rand(len(map["tasks"]), 3)
        for t, i in zip(map["tasks"], range(len(map["tasks"]))):
            x_s, y_s = t['start'][0], t['start'][1]
            self.tasks[t['task_name']] = [Rectangle((x_s - 0.25, y_s - 0.25), 0.5, 0.5, facecolor=task_colors[i], edgecolor='black', alpha=0)]
            self.patches.append(self.tasks[t['task_name']][0])
        for t, i in zip(map["tasks"], range(len(map["tasks"]))):
            x_g, y_g = t['goal'][0], t['goal'][1]
            self.tasks[t['task_name']].append(RegularPolygon((x_g, y_g - 0.05), 3, 0.2, facecolor=task_colors[i], edgecolor='black', alpha=0))
            self.patches.append(self.tasks[t['task_name']][1])

        # Create agents:
        self.T = 0
        # Draw goals first
        for d, i in zip(map["agents"], range(0, len(map["agents"]))):
            if 'goal' in d:
                self.patches.append(
                    Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black',
                              alpha=0.5))
        for d, i in zip(map["agents"], range(0, len(map["agents"]))):
            name = d["name"]
            self.agents[name] = Circle((d["start"][0], d["start"][1]), 0.3, facecolor=Colors[0], edgecolor='black')
            self.agents[name].original_face_color = Colors[0]
            self.patches.append(self.agents[name])
            self.T = max(self.T, schedule["schedule"][name][-1]["t"])
            self.agent_names[name] = self.ax.text(d["start"][0], d["start"][1], name.replace('agent', ''))
            self.agent_names[name].set_horizontalalignment('center')
            self.agent_names[name].set_verticalalignment('center')
            self.artists.append(self.agent_names[name])

        # self.ax.set_axis_off()
        # self.fig.axes[0].set_visible(False)
        # self.fig.axes.get_yaxis().set_visible(False)

        # self.fig.tight_layout()

        self.anim = animation.FuncAnimation(self.fig, self.animate_func,
                                            init_func=self.init_func,
                                            frames=int(self.T + 1) * 10,
                                            interval=10,
                                            blit=True,
                                            repeat=False)

    def save(self, file_name, speed):
        self.anim.save(
            file_name,
            "ffmpeg",
            fps=10 * speed,
            dpi=200),
        # savefig_kwargs={"pad_inches": 0, "bbox_inches": "tight"})

    def show(self):
        plt.show()

    def init_func(self):
        for p in self.patches:
            self.ax.add_patch(p)
        for a in self.artists:
            self.ax.add_artist(a)
        return self.patches + self.artists

    def animate_func(self, i):
        for agent_name, agent in self.combined_schedule.items():
            pos = self.getState(i / self.slow_factor, agent)
            p = (pos[0], pos[1])
            self.agents[agent_name].center = p
            self.agent_names[agent_name].set_position(p)

        # Reset all colors
        for _, agent in self.agents.items():
            agent.set_facecolor(agent.original_face_color)

        # Make tasks visible at the right time
        for t in map["tasks"]:
            if t['start_time'] <= i / self.slow_factor + 1 <= self.schedule['completed_tasks_times'][t['task_name']]:
                self.tasks[t['task_name']][0].set_alpha(0.5)
                self.tasks[t['task_name']][1].set_alpha(0.5)
            else:
                self.tasks[t['task_name']][0].set_alpha(0)
                self.tasks[t['task_name']][1].set_alpha(0)

        # Check drive-drive collisions
        agents_array = [agent for _, agent in self.agents.items()]
        for i in range(0, len(agents_array)):
            for j in range(i + 1, len(agents_array)):
                d1 = agents_array[i]
                d2 = agents_array[j]
                pos1 = np.array(d1.center)
                pos2 = np.array(d2.center)
                if np.linalg.norm(pos1 - pos2) < 0.7:
                    d1.set_facecolor('red')
                    d2.set_facecolor('red')
                    print("COLLISION! (agent-agent) ({}, {})".format(i, j))

        return self.patches + self.artists

    def getState(self, t, d):
        idx = 0
        while idx < len(d) and d[idx]["t"] < t:
            idx += 1
        if idx == 0:
            return np.array([float(d[0]["x"]), float(d[0]["y"])])
        elif idx < len(d):
            posLast = np.array([float(d[idx - 1]["x"]), float(d[idx - 1]["y"])])
            posNext = np.array([float(d[idx]["x"]), float(d[idx]["y"])])
        else:
            return np.array([float(d[-1]["x"]), float(d[-1]["y"])])
        dt = d[idx]["t"] - d[idx - 1]["t"]
        t = (t - d[idx - 1]["t"]) / dt
        pos = (posNext - posLast) * t + posLast
        return pos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-map", help="input file containing map")
    parser.add_argument("-schedule", help="schedule for agents")
    parser.add_argument('--video', dest='video', default=None,
                        help="output video file (or leave empty to show on screen)")
    parser.add_argument("--speed", type=int, default=1, help="speedup-factor")
    args = parser.parse_args()

    if args.map is None:
        with open(os.path.join(RoothPath.get_root(), 'config.json'), 'r') as json_file:
            config = json.load(json_file)
        args.map = os.path.join(RoothPath.get_root(), os.path.join(config['input_path'], config['input_name']))
        args.schedule = '../output.yaml'

    with open(args.map) as map_file:
        map = yaml.load(map_file, Loader=yaml.FullLoader)

    with open(args.schedule) as states_file:
        schedule = yaml.load(states_file, Loader=yaml.FullLoader)

    animation = Animation(map, schedule, slow_factor=3)

    # animation.save('TP_k=5.mp4', 1)

    if args.video:
        animation.save(args.video, args.speed)
    else:
        animation.show()


