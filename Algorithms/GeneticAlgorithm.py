from SpacePartitioning import binarySpacePartitioning
import logging
import utilityFunctions
import RNG

class Partition:
	def __init__(self, space, score):
		self.space = space
		self.score = score

def runGA(height_map, y_min, y_max, x_min, x_max,z_min,z_max):

	list_of_lots = generatePopulation(y_min, y_max, x_min, x_max,z_min,z_max, height_map, 20)

	for generation in range(0, 10):

		logging.warning("Running generation {}".format(generation))
		offspring = []

		logging.info("List of lots (sizes):")
		for lots in list_of_lots:
			logging.info(len(lots))		

		for i in range(5):
			parent1 = selection(list_of_lots)
			parent2 = selection(list_of_lots)
			logging.info("Parent1: {}".format(len(parent1)))
			logging.info("Parent2: {}".format(len(parent2)))

			child1, child2 = crossover(parent1, parent2)
			logging.info("Child1: {}".format(len(child1)))
			logging.info("Child2: {}".format(len(child2)))

			child1 = removeIntersections(child1)
			child2 = removeIntersections(child2)

			logging.info("Child1 after removing Intersection: {}".format(len(child1)))
			logging.info("Child2 after removing Intersection: {}".format(len(child2)))

			child1 = mutate(child1)
			child2 = mutate(child2)

			offspring.append(child1)
			offspring.append(child2)

		offspring.extend(generatePopulation(y_min, y_max, x_min, x_max,z_min,z_max, height_map, 10))
		for index in range(len(offspring)):
			orderByScore(offspring[index])

		list_of_lots = offspring

	return list_of_lots

def generatePopulation(y_min, y_max, x_min, x_max,z_min,z_max, height_map, length=20):
	list_of_lots = []

	for i in range(length):
		lots = []
		initial_partitioning = binarySpacePartitioning(y_min, y_max, x_min, x_max,z_min,z_max, [])

		# create Partition objects using the partitions returned from the algorithm
		for p in initial_partitioning:
			p_score = utilityFunctions.getScoreArea_type1(height_map, p[2], p[3], p[4], p[5]) 
			lots.append(Partition(p, p_score))

		logging.info("Generated partitioning (len:{}): ".format(len(lots)))
		removeInvalids(height_map, lots)
		orderByScore(lots)

		logging.info("Cleaned partitioning (len:{}): ".format(len(lots)))
		list_of_lots.append(lots)

	return list_of_lots


def getFitness(individual):
	score = 0
	for lot in individual:
		score += lot.score
	return score

def selection(population, tournament_size=5):
	tournament_individuals = RNG.choice(population, tournament_size)
	selected = tournament_individuals[0]
	best_fitness = getFitness(tournament_individuals[0])

	for individual in tournament_individuals:
		fitness = getFitness(individual)
		if fitness < best_fitness:
			best_fitness = fitness
			selected = individual

	return selected

def crossover(partitioning1, partitioning2):
	joint = []
	joint.extend(partitioning1)
	joint.extend(partitioning2)
	RNG.shuffle(joint)
	middle = len(joint)/2
	partitioning1 = joint[middle:]
	partitioning2 = joint[:middle]
	return (partitioning1, partitioning2)

def mutate(individual):
	# let's ignore mutation for now
	return individual

def logIndividual(lots):		
	log = "Population: "
	for l in lots: log += "{} ".format(l.score)
	logging.info(log)

# order a list of lots according to their steepness score
# maybe not be actually useful but for now stays here
def orderByScore(individual):
	individual.sort(key=lambda x: x.score)

# receives an individual and removes every partition does not meet the minimum
# size or that has invalid ground blocks (e.g. water, lava)
def removeInvalids(height_map, partitioning, minimum_h=10, minimum_w=16, minimum_d=16):

	for index in range(len(partitioning)-1, -1, -1):
		p = partitioning[index]
		(y_min, y_max, x_min, x_max, z_min, z_max) = p.space
		failed_conditions = [] 
		cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
		if cond1 == False: failed_conditions.append(1)
		cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, minimum_d)
		if cond2 == False: failed_conditions.append(2) 
		if not cond1 or not cond2:
			partitioning.pop(index)
			index -=1			

# receives an individual and removes every partition that intersects with another
def removeIntersections(partitioning):
	valid_partitioning = []
	valid_partitioning.append(partitioning.pop(0))

	for i in range(len(partitioning)-1, -1, -1):
		intersect = False

		for p in valid_partitioning:	
			if utilityFunctions.intersectPartitions(partitioning[i].space, p.space):
				#print("Intersection between ", partitioning[i].space, p.space)
				intersect = True
				break
		if intersect == False:
			valid_partitioning.append(partitioning.pop(i))

	return valid_partitioning
