import random
import math

def gen_tasks_and_delays(agents, starts, goals, n_tasks, task_freq, n_delays_per_agent, delay_interval=None):
    arrival_time = 0
    tasks = []
    delays = {}
    if delay_interval is None:
        delay_interval = n_tasks * 10

    for i in range(n_tasks):
        # Get the next probability value from Uniform(0,1)
        p = random.random()
        # Plug it into the inverse of the CDF of Exponential(task_freq)
        inter_arrival_time = -math.log(1.0 - p) / task_freq
        # Add the inter-arrival time to the running sum
        arrival_time = arrival_time + inter_arrival_time
        # Generate task
        tasks.append({'start_time': int(arrival_time), 'start': random.choice(starts), 'goal': random.choice(goals),
                      'task_name': 'task' + str(i)})

    for i in range(len(agents)):
        delays[agents[i]['name']] = random.sample(range(delay_interval), n_delays_per_agent)

    return tasks, delays
