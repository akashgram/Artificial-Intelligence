'''
@author: Akash Gopal
@date: 12/08/2015
'''
import math
import random
import pickle
import numpy as np
import pandas as pd
from scipy.stats import norm
from collections import defaultdict
from copy import deepcopy

def compute_fitness(world, population):
    '''
    This should return a scalar which is to be maximized.
    max_volume is the maximum volume that the knapsack can contain.
    volumes is a list containing the volume of each item in the knapsack.
    prices is a list containing the price of each item in the knapsack, which is aligned with 'volumes'.
    '''
    # Here, I wrote my own implementation of the compute fitness function
    # In this function, I have made a couple of changes as I followed the paper 
    # which was given to help us understand. Hence I directly called population 
    # instead of calling their subsequent volumes and prices.

    # Extracted max_volume, volumes and prices from world.
    max_volume = world[0]
    volumes = world[1]
    prices = world[2]
    # Fitness used to calculate the fitness of all the chromosomes in the population
    fitness = []
    
    for j in range(len(population)):
        # run this loop for every chromosome.
        total_volume = 0
        total_prices = 0
        flag = True
        for i in range(len(volumes)):
            # If the volume of chromosome in question is greater than the capacity of the
            # knapsack, then one of the bits in that chromosome whose value is 1 is inverted
            # and chromosome is checked again.
            if total_volume + (volumes[i]*population[j][i]) > max_volume:
                flag = True
                while flag == True:
                   rand = random.randint(0,i)
                   if population[j][rand] != 0:
                        population[j][rand] = 0
                        if rand != i:
                            total_volume -= volumes[rand]
                            total_prices -= prices[rand]
                        flag = False   
            else:
                if population[j][i]!= 0:
                    total_volume += volumes[i]
                    total_prices += prices[i]
        fitness.append(total_prices)          
    return (fitness, population)

def randomSelection(population,fitnesses):
    '''
    This should return a single chromosome from the population. The selection process should be random, but with weighted probabilities proportional
    to the corresponding 'fitnesses' values.
    '''
    # I have used group selection wherein I have an index array which keeps track of 
    # the index of each of the chromosomes when after it has been sorted.
    temp = []
    temp.append(deepcopy(fitnesses))
    rand1 = random.randint(1, 100)
    index = sorted(range(len(fitnesses)), key=lambda k: temp[0][k], reverse = True)
    temp[::-1].sort()
    length = len(fitnesses)

    # we randomly choose an item from the first quarter of the sorted fitnesses with 50% probability
    if (rand1 >= 1 and rand1 <= 50):
        rand2 = random.randint(0, (length/4)-1)
        return population[index[rand2]]
    # we randomly choose an item from the second quarter of the sorted fitnesses with 30% probability
    elif (rand1 > 50 and rand1 <= 80):
        rand2 = random.randint((length/4), ((2 *(length/4)) - 1))
        return population[index[rand2]]
    # we randomly choose an item from the third quarter of the sorted fitnesses with 15% probability
    elif (rand1 > 80 and rand1 <= 95):
        rand2 = random.randint(2 *(length/4), (3*(length/4))-1)
        return population[index[rand2]]
    # we randomly choose an item from the fourth quarter of the sorted fitnesses with 5% probability
    else:
        rand2 = random.randint((3*(length/4)), length-1)
        return population[index[rand2]]

def reproduce(mom,dad):
    "This does genetic algorithm crossover. This takes two chromosomes, mom and dad, and returns two chromosomes."  
    # choosing the crossover index
    rand = random.randint(1,len(mom)-2)
    temp = mom * 1
    while(rand < len(mom)):
        mom[rand] = dad[rand]
        dad[rand] = temp[rand]
        rand +=1
    return mom,dad

def mutate(child):
    "Takes a child, produces a mutated child."
    # 0.02% probability that each bit gets mutated
    for i in range(len(child)):
        rand = random.randint(1,50)
        if rand == 1:
            if(child[i] == 1):
                child[i] = 0
            else:
                child[i] = 1
    return child

def genetic_algorithm(world,popsize,max_years,mutation_probability):
    '''
    world is a data structure describing the problem to be solved, which has a form like 'easy' or 'medium' as defined in the 'run' function.
    The other arguments to this function are what they sound like.
    genetic_algorithm *must* return a list of (chromosomes,fitnesses) tuples, where chromosomes is the current population of chromosomes, and fitnesses is
    the list of fitnesses of these chromosomes. 
    '''
    fitness = []
    new_chromosomes = [] 
    final_list_chromosomes = []   
    # Step 1: Initialize the first population by randomly generating population of Size chromosomes
    chromosomes = np.random.randint(2, size=(popsize, len(world[1])))
    # Counter to keep number of generations
    num_years = 0
    new_chromosomes = chromosomes
    flag = True

    while num_years < max_years:
        #Step 2: Calculate the fitness and volume of all chromosomes
        fitness, new_chromosomes = compute_fitness(world, new_chromosomes)
        temp = []
        temp.append(deepcopy(new_chromosomes))
        temp.append(deepcopy(fitness))
        final_list_chromosomes.append(deepcopy(temp))
        fitness = np.array(fitness)
        # finding the majority value and count of the majority value
        d = defaultdict(int)
        for i in fitness:
            d[i] += 1
        result = max(d.iteritems(), key=lambda x: x[1])
        count = result[1]
        ratio = count/float(len(fitness))
        # Step 3: Check what percentage of the chromosomes in the population has the same fitness value
        # If greater than 90%, then return the value.
        if ratio < 0.9:
            i = 0
            temp_chromosomes=[]
            length = popsize/2
            while (i < length):
                # Step 4: Randomly select 2 chromosomes from the population 
                chrome1 = randomSelection(new_chromosomes,fitness)
                chrome2 = randomSelection(new_chromosomes,fitness)
                i += 1
                # Step 5: Performing crossover on the 2 chromosomes selected
                temp_chrome1,temp_chrome2 = reproduce(chrome1,chrome2)
                # Step 6: Performing mutation on the chromosomes obtained
                new_chrome1 = mutate(temp_chrome1)
                new_chrome2 = mutate(temp_chrome2)
                
                # Creating a new population
                temp_chromosomes.append(deepcopy(new_chrome1))
                temp_chromosomes.append(deepcopy(new_chrome2))
            new_chromosomes = []
            # Re-Initializing the old population with the new ones
            new_chromosomes = temp_chromosomes
        elif ratio >= 0.9:
            break
        num_years +=1

    return final_list_chromosomes

def run(popsize,max_years,mutation_probability):
    '''
    The arguments to this function are what they sound like.
    Runs genetic_algorithm on various knapsack problem instances and keeps track of tabular information with this schema:
    DIFFICULTY YEAR HIGH_SCORE AVERAGE_SCORE BEST_PLAN
    '''
    table = pd.DataFrame(columns=["DIFFICULTY", "YEAR", "HIGH_SCORE", "AVERAGE_SCORE", "BEST_PLAN"])
    sanity_check = (10, [10, 5, 8], [100,50,80])
    chromosomes = genetic_algorithm(sanity_check,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'sanity_check', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    # print table
    # Answer: 15
    easy = (20, [20, 5, 15, 8, 13], [10, 4, 11, 2, 9])
    chromosomes = genetic_algorithm(easy,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'easy', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    # print table
    # Answer: 163
    medium = (100, [13, 19, 34, 1, 20, 4, 8, 24, 7, 18, 1, 31, 10, 23, 9, 27, 50, 6, 36, 9, 15],
                   [26, 7, 34, 8, 29, 3, 11, 33, 7, 23, 8, 25, 13, 5, 16, 35, 50, 9, 30, 13, 14])
    chromosomes = genetic_algorithm(medium,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'medium', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    # print table
    hard = (5000, norm.rvs(50,15,size=100), norm.rvs(200,60,size=100))
    chromosomes = genetic_algorithm(hard,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'hard', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    for difficulty_group in ['sanity_check','easy','medium','hard']:
        group = table[table['DIFFICULTY'] == difficulty_group]
        bestrow = group.ix[group['HIGH_SCORE'].argmax()]
        print("Best year for difficulty {} is {} with high score {} and chromosome {}".format(difficulty_group,int(bestrow['YEAR']), bestrow['HIGH_SCORE'], bestrow['BEST_PLAN']))
    table.to_pickle("results.pkl") #saves the performance data, in case you want to refer to it later. pickled python objects can be loaded back at any later point.
    #print table

def main():
    popsize = 30 # Size of the population
    max_years = 100 # Number of generations to be iterated through
    mutation_probability = 0.02 # Mutation Probablity of each bit of a chromosome
    run(popsize,max_years,mutation_probability) # calling the run function


''' Start of the program '''
if __name__ == "__main__" : main()