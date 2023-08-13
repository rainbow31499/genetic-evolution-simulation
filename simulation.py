from main import Environment
import numpy as np
import string
import matplotlib.pyplot as plt
from settings import *

e = Environment()

e.initialize_population(initial_population)

population = np.zeros([0,2])
number_of_lineages = np.zeros([0,2])
resources = {letter: np.array([]) for letter in string.ascii_lowercase}
max_population = {}
first_generation_survived = {}
total_generations_survived = {}
population_record_by_lineage = {}

def record_data(e):
    global population, resources, max_population, first_generation_survived, total_generations_survived, population_record_by_lineage, number_of_lineages
    population = np.concatenate([population, np.array([[e.generation, len(e.individuals)]])], axis=0)

    for letter in string.ascii_lowercase:
        resources[letter] = np.append(resources[letter], e.resources[letter])

    current_population = {}

    for individual in e.individuals:
        if individual.lineage not in max_population:
            max_population[individual.lineage] = 0

        if individual.lineage not in first_generation_survived:
            first_generation_survived[individual.lineage] = e.generation

        if individual.lineage not in total_generations_survived:
            total_generations_survived[individual.lineage] = 0

        if individual.lineage not in population_record_by_lineage:
            population_record_by_lineage[individual.lineage] = np.array([])

        if individual.lineage not in current_population:
            current_population[individual.lineage] = 0

        current_population[individual.lineage] += 1

    for lineage in current_population:
        population_record_by_lineage[lineage] = np.append(population_record_by_lineage[lineage], np.array([current_population[lineage]]))

        total_generations_survived[lineage] += 1

        if current_population[lineage] > max_population[lineage]:
            max_population[lineage] = current_population[lineage]
    
    current_lineages = len(current_population)
    number_of_lineages = np.concatenate([number_of_lineages, np.array([[e.generation, current_lineages]])])

    def keep(lineage):
        if lineage[0] in current_population:
            return True
        if max_population[lineage[0]] >= 10:
            return True
        return False
    
    first_generation_survived = dict(filter(keep, first_generation_survived.items()))
    total_generations_survived = dict(filter(keep, total_generations_survived.items()))
    population_record_by_lineage = dict(filter(keep, population_record_by_lineage.items()))
    max_population = dict(filter(keep, max_population.items()))

record_data(e)

for i in range(number_of_generations):
    e.run_generation()
    record_data(e)
    if len(e.individuals) == 0:
        break

def keep(lineage):
    if max_population[lineage[0]] >= 10:
        return True
    return False

first_generation_survived = dict(filter(keep, first_generation_survived.items()))
total_generations_survived = dict(filter(keep, total_generations_survived.items()))
population_record_by_lineage = dict(filter(keep, population_record_by_lineage.items()))
max_population = dict(filter(keep, max_population.items()))

print('Maximum population:')
ranked_max_population = sorted(list(map(lambda tup: (tup[1], tup[0]), max_population.items())), reverse=True)
for lineage in ranked_max_population[:20]:
    print(lineage[1], lineage[0])

print('Genome strings of top 10 survivors:')
for lineage in ranked_max_population[:10]:
    print(lineage[1], e.genomes[lineage[1]], lineage[0])

print('Characteristics of top 10 survivors:')
for lineage in ranked_max_population[:10]:
    print(lineage[1], lineage[0], e.lineage_characteristics[lineage[1]])

print('Final resources available (ranked by letter):')
ranked_resources = sorted(list(map(lambda tup: (tup[1], tup[0]), e.resources.items())), reverse=True)
for letter in ranked_resources:
    print(letter[1], letter[0])

fig, axs = plt.subplots(nrows=2, ncols=2)

axs[0][0].plot(population[:,0], population[:,1], '-')

for letter in resources:
    axs[0][1].plot(resources[letter], '-')
axs[0][1].legend(resources)

for entry in ranked_max_population:
    lineage = entry[1]
    length = len(population_record_by_lineage[lineage])
    x = np.arange(first_generation_survived[lineage], first_generation_survived[lineage]+length)
    axs[1][0].plot(x, population_record_by_lineage[lineage])
axs[1][0].legend([entry[1] for entry in ranked_max_population])

axs[1][1].plot(number_of_lineages[:,0], number_of_lineages[:,1], '-')

plt.show()