from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
from BinarySpacePartitioning import binarySpacePartitioning
from HouseGenerator import generateHouse
from MultistoreyBuildingGenerator import generateBuilding, generateHospital
import pickle

inputs = (
	("House Generator", "label"),
	("Walls Material Type", alphaMaterials.DoubleStoneSlab),
	("Walls Material Subtype (min)", 11),
	("Walls Material Subtype (max)", 15),
	("Ceiling Material Type", alphaMaterials.WoodPlanks),
	("Ceiling Material Subtype (min)", 1),
	("Ceiling Material Subtype (max)", 5)
	)

def perform(level, box, options, height_map=None):

	# PREPARATION
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})

	# calculate height map if not passed as param
	if height_map == None:
		height_map = utilityFunctions.getHeightMap(level,box)
	
	# PARTITIONING OF NEIGHBOURHOODS
	(center, neighbourhoods) = generateNeighbourhoodPartitioning(world_space, height_map)

	# GENERATING CITY CENTER
	all_lots = []
	all_buildings = []
	space = utilityFunctions.dotdict({"y_min": center[0], "y_max": center[1], "x_min": center[2], "x_max": center[3], "z_min": center[4], "z_max": center[5]})
	print("City Center Space: ")
	print(space)
	partitioning_list = generatePartitionings(space, 35, 20)
	partitioning_list = removeInvalidPartitionsFromPartitionings(partitioning_list, height_map)
	partitioning = selectBestPartition(partitioning_list)
	print("City Center: ")
	for p in partitioning:
		print (p)
	buildings = fillBuildings(level, box, matrix, height, width, depth, partitioning, height_map, options)
	all_buildings.extend(buildings)
	all_lots.extend(partitioning)

	# GENERATING NEIGHBOURHOODS
	for partitioning in neighbourhoods:
		space = utilityFunctions.dotdict({"y_min": partitioning[0], "y_max": partitioning[1], "x_min": partitioning[2], "x_max": partitioning[3], "z_min": partitioning[4], "z_max": partitioning[5]})
		print("Neighbourhood Space: ")
		print(space)
		partitioning_list = generatePartitionings(space)
		partitioning_list = removeInvalidPartitionsFromPartitionings(partitioning_list, height_map)
		partitioning = selectBestPartition(partitioning_list)
		print("neighbourhoods: ")
		for p in partitioning:
			print (p)
		houses = fillHouses(level, box, matrix, height, width, depth, partitioning, height_map, options)
		all_buildings.extend(houses)
		all_lots.extend(partitioning)

	# GENERATE A PATH MAP TO FIND ROADS BETWEEN BUILDINGS
	pathMap = utilityFunctions.getPathMap(height_map, width, depth)
	print("Path Map:")
	for z in range(depth):
		for x in range(width):
			print(x, z, pathMap[x][z])
		
	pavementBlockID = 171
	pavementBlockSubtype = random.randint(0, 14)
	#MST = utilityFunctions.getMST(all_lots)
	MST = utilityFunctions.getMST(all_buildings)
	print("Final MST: ")
	for m in MST:
		print(m)
	for m in MST:
		print("Pavement between ", m[0], m[1])
		p1 = m[0]
		p2 = m[1]
		#p1_center = utilityFunctions.getCentralPoint(p1[2],p1[3],p1[4],p1[5])
		#p2_center = utilityFunctions.getCentralPoint(p2[2],p2[3],p2[4],p2[5])
		p1_entrancePoint = p1.entranceLot
		p2_entrancePoint = p2.entranceLot
		#utilityFunctions.pavementConnection(matrix, p1_center[0], p1_center[1], p2_center[0], p2_center[1], height_map, (pavementBlockID, pavementBlockSubtype))
		utilityFunctions.pavementConnection(matrix, p1_entrancePoint[1], p1_entrancePoint[2], p2_entrancePoint[1], p2_entrancePoint[2], height_map, (pavementBlockID, pavementBlockSubtype))


	

	# UPDATE WORLD
	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

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
		utilityFunctions.updateHeightMap(height_map, p[2], p[3], p[4], p[5], flattened_height)
		h = utilityFunctions.convertHeightCoordinates(box, height, flattened_height)
	else:
		heightCounts = utilityFunctions.getHeightCounts(height_map, p[2],p[3], p[4], p[5])
		most_ocurred_height = max(heightCounts, key=heightCounts.get)
		#print("Non flattened height: ", most_ocurred_height)
		utilityFunctions.updateHeightMap(height_map, p[2], p[3], p[4], p[5], most_ocurred_height)
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


def generatePartitionings(space, partition_min=30, valid_min=15, number_of_tries=10):

	partitioning_list = []
	for i in range(number_of_tries):
		#partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, partition_min=partition_min, valid_min=valid_min)
		partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [], partition_min=partition_min, valid_min=valid_min)
		partitioning_list.append(partitioning)
	return partitioning_list

def generateNeighbourhoodPartitioning(space, height_map):
	neighbourhoods = []
	center = utilityFunctions.getSubsection(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.6)
	partitions = utilityFunctions.subtractPartition((space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max), center)
	for p in partitions:
		neighbourhoods.append(p)
	return (center, neighbourhoods)

def removeInvalidPartitionsFromPartitionings(partitioning_list, height_map):
	valid_partitioning_list = []
	for partitioning in partitioning_list:
		valid_partitioning = cleanPartition(partitioning, height_map)
		valid_partitioning_list.append(valid_partitioning)
	return valid_partitioning_list

def cleanPartition(partitioning, height_map):
	valid_partitioning = []
	for p in partitioning:
		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map) == True:
			valid_partitioning.append(p)
	return valid_partitioning

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

# Gets a list of partitionings and returns the best one 
# based on some criteria (currently the one with highest
# number of valid lots)
def selectBestPartition(partitioning_list):
	partitioning_sizes = []
	for partitioning in partitioning_list:
		partitioning_sizes.append((len(partitioning), partitioning))
	partitioning_list = sorted(partitioning_sizes, reverse=True)
	return partitioning_list[0][1]

def settlementGenerator(level, box, matrix, height, width, depth, partitioning, height_map, options):
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

def fillBuildings(level, box, matrix, height, width, depth, partitioning, height_map, options):
	buildings = []
	for p in partitioning:
		#print(p[0],p[1],p[2],p[3], p[4], p[5])	
		#if random.random() > 0.5:
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		buildings.append(generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options))
		utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-1, p[4]+1, p[5]-1, -1)
	return buildings

def fillHouses(level, box, matrix, height, width, depth, partitioning, height_map, options):
	ceilingBlockID = 171
	ceilingBlockSubtype = random.randint(0, 14)
	houses = []
	for p in partitioning:
		#print(p[0],p[1],p[2],p[3], p[4], p[5])
		#if random.random() > 0.5:	
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		houses.append(generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options, (ceilingBlockID, ceilingBlockSubtype)))
		utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-1, p[4]+1, p[5]-1, -1)
	return houses

#
# Old settlement generator function
# 
#def perform_basic(level, box, options):
#
#	# PREPARATION
#	(width, height, depth) = utilityFunctions.getBoxSize(box)
#	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
#	height_map = utilityFunctions.getHeightMap(level,box)
#	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})
#
#	# PARTITION SPACE
#	partitioning_list = generatePartitioning(world_space)
#	partitioning_list = removeInvalidPartitionsFromPartitionings(partitioning_list, height_map)
#	partitioning = selectBestPartition(partitioning_list)
#
#	# BUILDINGS GENERATION
#	settlementGenerator_basic(level, box, matrix, height, width, depth, partitioning, height_map, options)
#
#	# UPDATE WORLD
#	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)
#
#def settlementGenerator_basic(level,box,matrix, height, width, depth, height_map, options):
#	(width, height, depth) = utilityFunctions.getBoxSize(box)
#	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
#	
#	partitions = generatePartitions(0, height-1, 0, width-1, 0, depth-1, height_map)
#
#	for p in partitions:
#		#print(p[0],p[1],p[2],p[3], p[4], p[5])
#		
#		#if random.random() > 0.5:
#		if random.random() > 0.8:
#			h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
#			generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
#		else:
#			#p = utilityFunctions.getSubsection(p[0],p[1],p[2],p[3], 0.5)
#			h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
#			generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
#
#	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)
#
## Attempts to perform partitioning of a given area number_of_tries times
## and returns the partitioning with the highest number of valid areas
#def generatePartitions(y_min, y_max, x_min, x_max, z_min, z_max, height_map, number_of_tries=50):
#
#	partitioning_list = []
#	for i in range(number_of_tries):
#		partition = generateAndValidatePartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map)
#		partitioning_list.append((len(partition), partition))
#
#	partitioning_list = sorted(partitioning_list, reverse=True)
#
#	#print("Checking all partitions!")
#	#for partitions in partitioning_list:
#	#	print("====== Valid Areas: ", partitions[0])
#
#	return partitioning_list[0][1]
#
## Perform binary partitioning of a given area between x_min, x_max and
# z_min, z_max. Returns a list with only valid partitions
#def generateAndValidatePartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map):
#	partition = []
#	initial_partitioning = binarySpacePartitioning(y_min, y_max, x_min, x_max, z_min, z_max)
#
#	for p in initial_partitioning:
#		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map) == True:
#			partition.append(p)
#
#	return partition
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