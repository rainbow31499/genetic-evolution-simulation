import string
import numpy as np
import random
from settings import *

class Individual:
    def __init__(self, genome, lineage, survival, reproduction, replace, insertion, deletion):
        self.genome = genome # String of letters between 35 and 85 characters
        self.lineage = lineage # Name of the lineage, such as 7 or 15.2 or 15.2.1
        self.survival = survival # Probability of survival in generation
        self.reproduction = reproduction # Expected reproduction number, Poisson random variable
        # Mutation probabilities during reproduction:
        self.replace = replace # Probability of replacing a single letter
        self.insertion = insertion # Probability of insertion of a random letter at a position
        self.deletion = deletion # Probability of deletion of a single letter (mutually exclusive with mutation)
        self.alive = True # Is this individual surviving this generation?

    def mutate_string(self):
        original_string = self.genome

        mutated = False

        new_string = ''

        for position in range(len(original_string)):
            while True:
                random_number = random.random()

                if random_number < self.insertion:
                    new_string += random.choice(string.ascii_lowercase)
                    mutated = True
                else:
                    break

            random_number = random.random()

            if random_number < self.replace:
                current_letter = original_string[position]
                selected_letter = current_letter
                while selected_letter == current_letter:
                    selected_letter = random.choice(string.ascii_lowercase)
                new_string += selected_letter
                mutated = True
                
            elif random_number < self.replace + self.deletion:
                mutated = True

            else:
                new_string += original_string[position]

        while True:
            random_number = random.random()

            if random_number < self.insertion:
                new_string += random.choice(string.ascii_lowercase)
                mutated = True
            else:
                break

        return new_string, mutated

class Environment:
    def __init__(self, resources={letter: initial_resources for letter in string.ascii_lowercase}):
        self.individuals = []
        self.resources = resources
        self.generation = 0
        self.mutations = {}
        self.genomes = {}
        self.lineage_characteristics = {}

    def produce_individual(self, genome_string, lineage, survival=None, reproduction=None, replace=None, insertion=None, deletion=None):
        if allowed_genome_length[0] <= len(genome_string) <= allowed_genome_length[1]:
            if survival == None:
                survival = random.uniform(survival_probability_range[0], survival_probability_range[1])
            if reproduction == None:
                reproduction=np.random.exponential(average_reproduction_number)
            if replace == None:
                replace=random.uniform(replace_probability_range[0], replace_probability_range[1])
            if insertion == None:
                insertion=random.uniform(insertion_probability_range[0], insertion_probability_range[1])
            if deletion == None:
                deletion=random.uniform(deletion_probability_range[0], deletion_probability_range[1])

            individual = Individual(genome_string, lineage, survival, reproduction, replace, insertion, deletion)
            if lineage not in self.genomes:
                self.genomes[lineage] = genome_string
            if lineage not in self.lineage_characteristics:
                self.lineage_characteristics[lineage] = {'Survival rate': survival,
                                                        'Reproductive number': reproduction,
                                                        'Replace probability': replace,
                                                        'Insertion probability': insertion,
                                                        'Deletion probability': deletion}

            letters_present = {letter: 0 for letter in string.ascii_lowercase}
            
            for letter in genome_string:
                letters_present[letter] += 1

            if all([letters_present[letter] <= self.resources[letter] for letter in string.ascii_lowercase]):
                for letter in string.ascii_lowercase:
                    self.resources[letter] -= letters_present[letter]
                self.individuals.append(individual)

    def initialize_population(self, starting_individuals):
        for i in range(starting_individuals):
            genome_string = ''
            for letter in range(random.randint(allowed_genome_length[0], allowed_genome_length[1])):
                genome_string += random.choice(string.ascii_lowercase)
            
            self.produce_individual(genome_string, str(i+1))

    def run_generation(self):
        self.generation += 1
        random.shuffle(self.individuals)
        for i in range(len(self.individuals)):
            individual = self.individuals[i]
            number_of_offspring = np.random.poisson(individual.reproduction)
            for j in range(number_of_offspring):
                new_genome = individual.mutate_string()
                if new_genome[1] == True:
                    if individual.lineage not in self.mutations:
                        self.mutations[individual.lineage] = 0
                    self.mutations[individual.lineage] += 1
                    new_lineage = individual.lineage + '.' + str(self.mutations[individual.lineage])
                    self.produce_individual(new_genome[0], new_lineage)
                else:
                    self.produce_individual(new_genome[0], individual.lineage, individual.survival, individual.reproduction, individual.replace, individual.insertion, individual.deletion)
            
            survival = random.random()
            if survival < individual.survival:
                pass
            else:
                individual.alive = False
        
        for individual in self.individuals:
            if individual.alive == False:
                for letter in individual.genome:
                    self.resources[letter] += 1
        
        self.individuals = list(filter(lambda i: i.alive == True, self.individuals))