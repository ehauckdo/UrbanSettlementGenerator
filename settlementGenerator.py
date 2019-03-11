from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
from BinarySpacePartitioning import binarySpacePartitioning
from HouseGenerator import generateHouse
from MultistoreyBuildingGenerator import generateBuilding, generateHospital

inputs = (
	("House Generator", "label"),
	("Walls Material Type", alphaMaterials.DoubleStoneSlab),
	("Walls Material Subtype (min)", 11),
	("Walls Material Subtype (max)", 15),
	("Ceiling Material Type", alphaMaterials.WoodPlanks),
	("Ceiling Material Subtype (min)", 1),
	("Ceiling Material Subtype (max)", 5)
	)

def perform_old(level, box, options):

	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	height_map = utilityFunctions.getHeightMap(level,box)

	settlementGenerator(level,box, matrix, height, width, depth, height_map, options)
	#hospitalSettlementGenerator(level, box, matrix, height, width, depth, height_map, options)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

def perform(level, box, options):

	# PREPARATION
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	height_map = utilityFunctions.getHeightMap(level,box)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})

	# PARTITION SPACE
	partitioning_list = generatePartitions_mod(world_space)
	partitioning_list = cleanPartitions_mod(partitioning_list, height_map)
	partitioning = selectBestPartition_mod(partitioning_list)

	#central_partitioning = getCentralPartition(world_space, height_map)
	#central_partition = central_partitioning[0]

	#print("Central Partitioning: ")
	#print(central_partitioning[0])

	#print("Other partitions: ")
	#for p in central_partitioning:
	#	print(p)

	#central_space = utilityFunctions.dotdict({"y_min": central_partitioning[0], "y_max": central_partitioning[1], "x_min": central_partitioning[2], "x_max": central_partitioning[3], "z_min": central_partitioning[4], "z_max": central_partitioning[5]})
	#partitioning_list = generatePartitions_mod(central_space)
	#partitioning_list = cleanPartitions_mod(partitioning_list, height_map)
	#partitioning = selectBestPartition_mod(partitioning_list)

	#fillBuildings_mod(level, box, matrix, partitioning, height_map, options)
	#central_partitioning.pop(0)
	#fillHouses_mod(level, box, matrix, central_partitioning, height_map, options)

	# BUILDINGS GENERATION
	settlementGenerator_mod(level, box, matrix, partitioning, height_map, options)


	# UPDATE WORLD
	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

def settlementGenerator(level,box,matrix, height, width, depth, height_map, options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	
	partitions = generatePartitions(0, height-1, 0, width-1, 0, depth-1, height_map)

	for p in partitions:
		#print(p[0],p[1],p[2],p[3], p[4], p[5])
		
		#if random.random() > 0.5:
		if random.random() > 0.8:
			h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
			generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
		else:
			#p = utilityFunctions.getSubsection(p[0],p[1],p[2],p[3], 0.5)
			h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
			generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

def hospitalSettlementGenerator(level, box, matrix, height, width, depth, height_map, options):

	partitions = hospitalSettlementGeneratePartitioning(height,0, width-1, 0, depth-1, height_map)
	for p in partitions:
		print(p)

	hp = partitions[0]
	h = prepareLot(level, box, matrix, height, width, depth, hp, height_map)

	generateHospital(matrix, h, hp[1],hp[2],hp[3], hp[4], hp[5], options)

	for i in range(1, len(partitions)):
		p = partitions[i]
		#if random.random() > 0.5:
		print("Building on partition ", p)
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		generateHouse(matrix, h,p[1],p[2],p[3],p[4],p[5], options)

	return matrix

def hospitalSettlementGeneratePartitioning(height, x_min, x_max, z_min, z_max, height_map):
	partitions = []

	hospitalPartition = utilityFunctions.getSubsection(x_min, x_max, z_min, z_max, 0.4)
	partitions.append(hospitalPartition)

	neighbourhoods = utilityFunctions.subtractPartition((x_min, x_max, z_min, z_max), hospitalPartition)
	for n in neighbourhoods:
		#neighbourhood_partitioning = binarySpacePartitioning(n[0], n[1], n[2], n[3], [])
		neighbourhood_partitioning = generatePartition(height, n[0], n[1], n[2], n[3], height_map)
		for p in neighbourhood_partitioning:
			partitions.append(p)

	return partitions

def getCentralPartition(space, height_map):
	partitions = []

	hospitalPartition = utilityFunctions.getSubsection(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.4)
	partitions.append(hospitalPartition)

	neighbourhoods = utilityFunctions.subtractPartition((space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max), hospitalPartition)
	for n in neighbourhoods:
		#neighbourhood_partitioning = binarySpacePartitioning(n[0], n[1], n[2], n[3], [])
		neighbourhood_partitioning = generatePartition(space.y_min, space.y_max, n[0], n[1], n[2], n[3], height_map)
		for p in neighbourhood_partitioning:
			partitions.append(p)

	return partitions


# ==========================================================================
#				# LOT PREPARING FUNCTIONS
# ==========================================================================

# Perform earthworks on a given lot, returns the height to start construction
def prepareLot(level, box, matrix, height, width, depth, p, height_map):
	areaScore = utilityFunctions.getScoreArea_type1(height_map, p[2],p[3], p[4], p[5], height_map[p[2]][p[4]])
	#print("Area score: ", areaScore)

	if areaScore != 0:
		flattened_height = flattenPartition(matrix, level, box, height, width, depth, p[2],p[3], p[4], p[5], height_map)
		#print("Flattened height: ", flattened_height)
		h = utilityFunctions.convertHeightCoordinates(box, height, flattened_height)
	else:
		heightCounts = utilityFunctions.getHeightCounts(height_map, p[2],p[3], p[4], p[5])
		most_ocurred_height = max(heightCounts, key=heightCounts.get)
		#print("Non flattened height: ", most_ocurred_height)
		h = utilityFunctions.convertHeightCoordinates(box, height, most_ocurred_height)

	return h

# Given the map matrix, a partition (x_min, x_max, z_min, z_max) and a
# height_map, perform earthworks on this lot by the flattening
# returns the height in which construction should start
def flattenPartition(matrix, level, box, height, width, depth, x_min, x_max, z_min, z_max, height_map):

	heightCounts = utilityFunctions.getHeightCounts(height_map, x_min, x_max, z_min, z_max)
	most_ocurred_height = max(heightCounts, key=heightCounts.get)

	#print("Height Counts: ", heightCounts)
	#print("Most ocurred height: ", most_ocurred_height)

	box_xmin = utilityFunctions.convertWidthMatrixToBox(box, width, x_min)
	box_zmin = utilityFunctions.convertDepthMatrixToBox(box, depth, z_min)
	#print("Reconverted coords: ", height_map[x_min][z_min], box_xmin, box_zmin)

	base_block = level.blockAt(box_xmin, height_map[x_min][z_min], box_zmin)
	#print("Base Block at coords ", x_min, x_max, ": ", base_block)

	for x in range(x_min, x_max):
		for z in range(z_min,z_max):
			if height_map[x][z] == most_ocurred_height:
				# Equal height! No flattening needed
				pass
			if height_map[x][z] != most_ocurred_height:
				#print(x, z, " Different Height!")

				if height_map[x][z] == -1:
					#print("Position ", x, z, " of height_map is -1. Cannot do earthworks.")
					continue

				matrix_height = utilityFunctions.convertHeightCoordinates(box, height, height_map[x][z])
				desired_matrix_height = utilityFunctions.convertHeightCoordinates(box, height, most_ocurred_height)
				#print("height_map[x][z] = ", height_map[x][z], ", matrix_height = ", matrix_height)
				#print("most_ocurred_height = ", most_ocurred_height, ", desired_matrix_height = ", desired_matrix_height)

				if desired_matrix_height > matrix_height:
					for y in utilityFunctions.twoway_range(matrix_height, desired_matrix_height):
						matrix[y][x][z] = base_block
				else:
					#update every block between top height and the desired height
					# when bringing the ground to a lower level, this will have the 
					# effect of e.g. erasing trees that were on top of that block
					# this may cause some things to be unproperly erased
					# (e.g. a branch of a tree coming from an nearby block)
					# but this is probably the best/less complex solution for this
					for y in utilityFunctions.twoway_range(height-1, desired_matrix_height+1):
						matrix[y][x][z] = 0
					matrix[desired_matrix_height][x][z] = base_block

	return most_ocurred_height

# ==========================================================================
#				# PARTITIONING FUNCTIONS
# ==========================================================================

# Attempts to perform partitioning of a given area number_of_tries times
# and returns the partitioning with the highest number of valid areas
def generatePartitions(y_min, y_max, x_min, x_max, z_min, z_max, height_map, number_of_tries=50):

	partitioning_list = []
	for i in range(number_of_tries):
		partition = generatePartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map)
		partitioning_list.append((len(partition), partition))

	partitioning_list = sorted(partitioning_list, reverse=True)

	#print("Checking all partitions!")
	#for partitions in partitioning_list:
	#	print("====== Valid Areas: ", partitions[0])

	return partitioning_list[0][1]

# Perform binary partitioning of a given area between x_min, x_max and
# z_min, z_max. Returns a list with only valid partitions
def generatePartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map):
	partition = []
	initial_partitioning = binarySpacePartitioning(y_min, y_max, x_min, x_max, z_min, z_max, [])

	for p in initial_partitioning:
		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map) == True:
			partition.append(p)

	return partition


# Check if a partition is valid according to some criteria
# Returns false if it does not pass one of the criterion
def isValidPartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map):

	cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
	#if cond1 == False: print("Failed Condition 1!")
	cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max)
	#if cond2 == False: print("Failed Condition 2!")
	cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, utilityFunctions.getScoreArea_type1)
	#if cond3 == False: print("Failed Condition 3!")
		
	return cond1 and cond2 and cond3


# =============================================================
#			MODUALR FUNCTIONS
# ============================================================

def generatePartitions_mod(space, number_of_tries=50):

	partitioning_list = []
	for i in range(number_of_tries):
		partitioning_list.append(generatePartition_mod(space))
	#	initial_partitioning = generatePartition_mod(space)
	#	partitioning = []

	#	for p in initial_partitioning:
	#		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map) == True:
	#			partitioning.append(p)

	#	partitioning_list.append((len(partitioning), partitioning))

	#partitioning_list = sorted(partitioning_list, reverse=True)

	#print("Checking all partitions!")
	#for partitions in partitioning_list:
	#	print("====== Valid Areas: ", partitions[0])

	#return partitioning_list[0][1]
	return partitioning_list

def generatePartition_mod(space, partitionings=50):

	partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])
	return partitioning

def cleanPartitions_mod(partitioning_list, height_map):
	valid_partitioning_list = []
	for partitioning in partitioning_list:
		#valid_partitioning = []
		#for p in partitioning:
		#	if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map) == True:
		#		valid_partitioning.append(p)
		valid_partitioning_list.append(cleanPartition_mod(partitioning, height_map))
	return valid_partitioning_list

def cleanPartition_mod(partitioning, height_map):
	valid_partitioning = []
	for p in partitioning:
		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map) == True:
			valid_partitioning.append(p)
	return valid_partitioning

def selectBestPartition_mod(partitioning_list):
	partitioning_sizes = []
	for partitioning in partitioning_list:
		partitioning_sizes.append((len(partitioning), partitioning))
	partitioning_list = sorted(partitioning_sizes, reverse=True)
	return partitioning_list[0][1]

def settlementGenerator_mod(level, box, matrix, partitioning, height_map, options):
	for p in partitioning:
		#print(p[0],p[1],p[2],p[3], p[4], p[5])
		
		#if random.random() > 0.5:
		if random.random() > 0.8:
			h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
			generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
		else:
			#p = utilityFunctions.getSubsection(p[0],p[1],p[2],p[3], 0.5)
			h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
			generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options)

def fillBuildings_mod(level, box, matrix, partitioning, height_map, options):
	for p in partitioning:
		#print(p[0],p[1],p[2],p[3], p[4], p[5])
		
		#if random.random() > 0.5:
		
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options)

def fillHouses_mod(level, box, matrix, partitioning, height_map, options):
	for p in partitioning:
		#print(p[0],p[1],p[2],p[3], p[4], p[5])
		
		#if random.random() > 0.5:
		#p = utilityFunctions.getSubsection(p[0],p[1],p[2],p[3], 0.5)
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options)

#
# Old function to pavament ground
#
# def pavementGround(level,box,options):
# 	(width, height, depth) = utilityFunctions.getBoxSize(box)
# 	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
#
# 	for x in range(0,width):
# 		for z in range(0,depth):
# 			matrix[0][x][z] = (1,0)
#
# 	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)
#
# Deprecated version of hospital settlement generator
# does not take into account ground levelling
#
#def hospitalSettlementGenerator(level,box,options):
#
#	(width, height, depth) = utilityFunctions.getBoxSize(box)
#	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
#
#	hospitalPartition = utilityFunctions.getSubsection(0, width-1, 0, depth-1, 0.4)
#	neighbourhoods = utilityFunctions.subtractPartition((0, width-1, 0, depth-1), hospitalPartition)
#
#	generateHospital(matrix, 0, height-1, hospitalPartition[0]+10, hospitalPartition[1]-10,hospitalPartition[2]+10,hospitalPartition[3]-10, options)
#
#	for n in neighbourhoods:
#		partitions = binarySpacePartitioning(n[0], n[1], n[2], n[3], [])
#
#		for p in partitions:
#		# 	getEuclidianDistancePartitions(p1, p2):
#
#			if random.random() > 0.5:
#				generateHouse(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)
#
#	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)