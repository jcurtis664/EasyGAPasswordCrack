import EasyGA
import random
import sys

password = sys.argv[1]				#password will be read from argv / USE: passwordCrack.py [password]
chromosome_length = len(password)	#chromosome_length for password_crack GA (one gene for each char)
iterations = 5						#number of times each password_crack GA runs
avgs = []							#average number of generations for each password_crack GA


#fitness function to crack password
def user_fitness_function(chromosome):

	fitness = 0
	
	#add 1 to fitness if a char is correct
	for i in range(len(password)):
		if (chromosome[i].value == ord(password[i])):
			fitness += 1
		
	return fitness

#termination function for fitness goal
def user_termination_function(ga):

	if ga.fitness_goal is not None and ga.population is not None:

		if ga.target_fitness_type == 'min' and ga.population[0].fitness <= ga.fitness_goal:
			return False

		elif ga.target_fitness_type == 'max' and ga.population[0].fitness >= ga.fitness_goal:
			return False

	return True

#returns string from array of ascii chars
def ascii_to_string(charList):
		
	string = ""
		
	for char in charList:
		string = string + chr(char.value)
			
	return string

#roulette parent selection function
def roulette(ga):

	parent_amount = int(ga.population_size * ga.parent_ratio)
	fitness_sum = sum(
		ga.get_chromosome_fitness(index)
		for index
		in range(len(ga.population))
	)

	if (fitness_sum != 0):
		probability = [ga.selection_probability]

		for index in range(len(ga.population)):
			probability.append(probability[-1]+ga.get_chromosome_fitness(index)/fitness_sum)

		probability = probability[1:]

		while len(ga.population.mating_pool) < parent_amount:

			rand_number = random.random()

			for index in range(len(probability)):
				if (probability[index] >= rand_number):
					ga.population.set_parent(index)
					break
	else:
		for i in range(parent_amount):
			ga.population.set_parent(i)

#fitness function for optimizeGA
def password_crack(optGA):

	avg = 0
	
	#run the ga 'iterations' times
	for j in range(iterations):
		
		#create a new GA
		ga = EasyGA.GA()

		ga.chromosome_length = chromosome_length
		ga.gene_impl = lambda: random.randint(33, 126)
		ga.population_size = 25
		ga.target_fitness_type = "max"
		
		ga.fitness_function_impl = user_fitness_function	#use user_fitness_function to crack password
		ga.termination_impl = user_termination_function		#use user_termination_function to stop when password is cracked
		ga.fitness_goal = chromosome_length					#only stop when whole password is cracked
		
		#replace ga values with optimizeGA values
		ga.parent_ratio = optGA.__getitem__(0).value
		ga.selection_probability = optGA.__getitem__(1).value
		ga.chromosome_mutation_rate = optGA.__getitem__(2).value
		ga.gene_mutation_rate = optGA.__getitem__(3).value
		ga.parent_selection_impl = optGA.__getitem__(4).value
		ga.crossover_individual_impl = optGA.__getitem__(5).value

		#evolve GA
		ga.evolve()

		print("the password is: " + ascii_to_string(ga.population[0]))

		ga.print_generation()
		ga.print_population()
		
		#add sum of generations it took to crack password
		avg += ga.current_generation
	
	print ("avg = " + str(avg / iterations))
	avgs.append(avg / iterations)
	return (avg / iterations)
	
#function to print optimizeGA chromosome
def print_chromosome(chromosome, num):

	print ("Chromosome - " + str(num) + " ")
	
	for i in chromosome:
		
		if isinstance(i.value, float):
			print (str(i))
		else:
			if i.value == EasyGA.Parent_Selection.Rank.tournament:
				print ("[EasyGA.Parent_Selection.Rank.tournament]")
			elif i.value == roulette:
				print ("[roulette]")
			elif i.value == EasyGA.Parent_Selection.Fitness.stochastic:
				print ("[EasyGA.Parent_Selection.Fitness.stochastic]")
			elif i.value == EasyGA.Crossover_Methods.Individual.single_point:
				print ("[EasyGA.Crossover_Methods.Individual.single_point]")
			elif i.value == EasyGA.Crossover_Methods.Individual.uniform:
				print ("[EasyGA.Crossover_Methods.Individual.uniform]")
			else:
				print ("Error: method is not a valid option")
		
	print (" / Fitness = " + str(chromosome.fitness))
	
#list of parent_selection_impl functions
parent_selection_impls = [EasyGA.Parent_Selection.Rank.tournament, roulette, EasyGA.Parent_Selection.Fitness.stochastic]
#list of crossover_individual_impl functions
crossover_individual_impls = [EasyGA.Crossover_Methods.Individual.single_point, EasyGA.Crossover_Methods.Individual.uniform]

#GA that optimizes password crack GA
optimizeGA = EasyGA.GA()

optimizeGA.chromosome_length = 6
optimizeGA.population_size = 5						#number of chromosomes(ga's) per generation
optimizeGA.generation_goal = 5						#number of generations
optimizeGA.target_fitness_type = 'min'
optimizeGA.chromosome_impl = lambda:	[
	random.uniform(0.05, 0.95),						#random value for parent_ratio
	random.uniform(0.25, 0.95),						#random value for selection_probability
	random.uniform(0.10, 0.50),						#random value for chromosome_mutation_rate
	random.uniform(0.05, 0.25),						#random value for gene_mutation_rate
	random.choice(parent_selection_impls),			#random choice for parent_selection_impl
	random.choice(crossover_individual_impls)		#random choice for crossover_individual_impl
]
optimizeGA.fitness_function_impl = password_crack	#fitness function based on how fast the GA cracks a password

optimizeGA.evolve()

optimizeGA.print_generation()

for i in range(0,optimizeGA.population_size):
	print_chromosome(optimizeGA.population[i], i)
	
for avg in avgs:
	print("avg: " + str(avg))

#graphs and displays the generation total fitnesses
optimizeGA.graph.generation_total_fitness()
optimizeGA.graph.show()