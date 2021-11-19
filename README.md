# Multi-Agent Pickup and Delivery
<p align="justify">
This repo contains implementations of various algorithms used to solve the problem of Multi-Agent Pickup and Delivery (a generalization of Multi-Agent Path Finding) and a simulation envirionment used to test them.
</p>

## Overview
<p align="justify">
Multi-Agent Pickup and Delivery (MAPD) is the problem of computing collision-free paths for a group of agents such that they can safely reach delivery locations from pickup ones.  These locations are provided at runtime, making MAPD a combination between classical Multi-Agent Path Finding (MAPF) and online task assignment. Current algorithms for MAPD do not consider many of the practical issues encountered in real applications: real agents often do not follow the planned paths perfectly, and may be subject to delays and failures.  The objectives of this work are to study the problem of MAPD with delays, and to present solution approaches that provide robustness guarantees by planning paths that limit the effects of imperfect execution. In particular, two  algorithms are introduced, k-TP and p-TP, both based on a decentralized algorithm typically used to solve MAPD, Token Passing  (TP), which offer deterministic and probabilistic guarantees,respectively. Experimentally, these algorithms are compared against a version of TP enriched with recovery routines. k-TP and p-TP, planning robustsolutions, are able to significantly reduce the number of replans caused by delays, with little or no increase in solution cost and running time.
</p>

## Simulation
In the image we can see an overview of the simulation pipeline. 
<p align="center">
    <img src="https://drive.google.com/uc?export=view&id=1V0kyAf4Xqcg0lJQ108vhEWzKEU4mdIBg" width="600" alt="Politecnico di Milano"/>
</p>
<p align="justify">
Green rectangles represents the input (a yaml file containing information about the environment, agents, tasks, delays) and the output (a json file containing the actual path walked by the agents) of the simulation. Blue rectangles constitute the core components of the simulation. The orange rectangular outline symbolizes the loop performed by advancing the simulation of one time step until all the tasks are completed. At every time step, the simulation manager calls the high level algorithm (k-TP or p-TP) to plan paths for the agents to complete available tasks; after the high level algorithm return the paths, agents are advanced of one step along their paths or remain in the current location depending on whether they are delayed at that time step or not. Also agents that would cause collisions by moving are stopped. Information about these delayed agents is given to the high level algorithm at the next time step. Finally, the purple rectangular outline represents the loop performed at any time step on all the agents that can be assigned to a task or that need a replan. When one of these agents is selected, he is assigned to the closest task according to Manhattan distance (in case of a replan task assignment is already done) and then the low level algorithm (in the code we can see two algorithms called, CBS and state-space A*, but in practice only state-space A* is used) is called to compute a path from the start location of the agent to the pickup vertex of task (in case of a replan, if an agent has already reached the pickup vertex this first path is empty) and then a path from the the pickup vertex to the goal vertex of the task.
</p>

## Requirements
The code has been tested with Python version 3.6.9.
All the packages needed to run the code can be found in the file *requirements.txt*. To install all the requirements, run the following code:

```
pip install -r requirements.txt
```

## Run One Simulation
<p align="justify">
Before running the simulation, an environment can be chosen. The <i>Environments</i> folder contains different predefined environments. There exists two main types of environments, differentiated by the presence or absence of the sub-string <i>_random</i> in the name. The ''random'' environments just specify the number of tasks and delay per agents, while the others present fixed tasks and delays (to use these environments, a special simulation parameter must be set). To change the simulation environment, open the file <i>config.json</i> and modify the parameter <i>''input_name</i> with the file name of the desired environment.
Then, to start the simulation, the script <i>demo.py</i> can be run. The script accepts various command line arguments:
 <ul>
    <li> <i>-k</i>: an integer (k >= 0) which represents the robustness parameter for k-TP; </li>
    <li> <i>-p</i>: a float (0 <= p <= 1) which represents the robustness parameter (probability threshold) for p-TP; </li>
    <li> <i>-pd</i>: a float (0 <= pd <= 1, default .02) which represents the expected probability of an agent of being delayed at any time step (used in p-TP); </li>
    <li> <i>-p_iter</i>: an integer (p_iter >= 1, default 1) which represents the number of times a new path can be recalculated if the one calculated before exceeds the probability threshold (used in p-TP); </li>
    <li> <i>-a_star_max_iter</i>: an integer (a_star_max_iter >= 1, default 5000) which represents the maximum number of states explored by the low-level algorithm state-space A*; </li>
    <li> <i>-slow_factor</i>: an integer (slow_factor >= 1, default 1) which allows to slow down the visualization; </li>
    <li> <i>-not_rand</i>: this parameter needs to be present if the input environment is not randomized. </li>
</ul>
Note that if the script is run without both k and p, it becomes TP with recovery routines. If the visualization does not start after the end of the simulation, the error could be related to the non-GUI back-end of Matplotlib. To resolve this problem, restart the simulation after the following code has been run:
</p>
    
```
sudo apt-get install python3-tk
```

In the following we present some example runs.
Run TP with recovery routines:

```
python3 demo.py
```

Run k-TP with k = 2 and slower visualization:

```
python3 demo.py -k 2 -slow_factor 3
```

Run p-TP with p = 0.6, pd = 0.05 in a non-randomized environment:

```
python3 demo.py -p 0.6 -pd 0.05 -not_rand
```

## Run Multiple Experiments
<p align="justify">
To run multiple experiments and collect all the statistics, a specific script, <i>run_all_experiments_new.py</i>, can be used. This script contains a list of experiments (easy to modify and extend) that will be run exploiting multi-threading; after all the experiments terminate a json file with the results will be saved in the <i>Experiments</i> folder. The script can be run with the following code:
</p>

```
python3 -m Utils.run_all_experiments_new
```
<p align="justify">
To see the results plotted as box plots, the script <i>plot_experiments</i> can be used. First, modify the file <i>config.json</i> changing the parameter <i>''experiments_name''</i> with the name of the experiments file that has just been created. Then run the visualization tool with the following code:
</p>

```
python3 -m Utils.plot_experiments
```

When a plot is closed, the next one will appear until the end of the experiments.
</p>
