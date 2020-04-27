# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 07:40:22 2020

@author: Philip du Toit
"""

from lib import CMAES
import numpy as np
from env_pong import Pong

num_params = 5
sigma_init = 0.1
population_size = 5
limit = 10000
n_episodes = 5


def func(x, theta):
    return 1 if x.dot(theta) > 0 else 0

def play_one_episode(env, params, render=False):
    observation = env.reset()
    t = 0
    cum_reward = 0
    
    while t < limit:
        action = func(observation, params)
        observation, reward, done, _ = env.step(action)
        if render:
            env.render()
        t += 1
        cum_reward += reward
        if done:
            break
    
    return t, cum_reward

def evaluate(env, params, n_episodes):
    episode_lengths = np.empty(n_episodes)
    episode_rewards = np.empty(n_episodes)
    
    for i in range(n_episodes):
        episode_lengths[i], episode_rewards[i] = play_one_episode(env, params)
        
    avg_episode_length = np.mean(episode_lengths)
    avg_episode_reward = np.mean(episode_rewards)
    
    return avg_episode_length, avg_episode_reward
        

def main():
    # Environment
    env = Pong()
    
    # CMA solver
    cma = CMAES(num_params, sigma_init=sigma_init, popsize=population_size)
    
    steps = 0
    average_fitness = 0

    while average_fitness < limit:
        # Ask the solver to provide candidate solutions
        solutions = cma.ask()
    
        # Create array to store fitness results
        fitness = np.zeros(cma.popsize)
    
        # Evaluate solutions
        for i in range(cma.popsize):
            fitness[i] = evaluate(env, solutions[i], n_episodes)[0]
            
        average_fitness = np.mean(fitness)
        maximum_fitness = np.max(fitness)
        # Send list of fitness results to solver
        cma.tell(fitness)
        
        # Receive best solution and fitness
        best_solution, _,  _, _ = cma.result()
        steps += 1
        if steps % 10 == 0:
            print("Step: %d, Average_fitness :%d, Best_fitness :%d"% (steps, average_fitness, maximum_fitness))
            
        if steps > 100:
            cma = CMAES(num_params, sigma_init=sigma_init, popsize=population_size)
            steps = 0
       
    print("Step: %d, Average_fitness :%d, Best_fitness :%d"% (steps, average_fitness, maximum_fitness))
    return best_solution

def test(params):
    env = Pong()
    play_one_episode(env, params, render=True)
    
if __name__ == "__main__":
    agent = np.array([-0.52565373,  0.44417123,  0.05475179, -0.16270629,  0.34118723])
    solution = main()
    test(solution)
    #test(agent)
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    