from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
import pickle
import RNG
import logging
from SpacePartitioning import binarySpacePartitioning, quadtreeSpacePartitioning
from HouseGenerator import generateHouse
from MultistoreyBuildingGenerator import generateBuilding, generateHospital

logging.basicConfig(filename="log", level=logging.INFO, filemode='w')
#logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger("pymclevel").setLevel(logging.WARNING)

def perform_new(level, box, options, height_map=None):
	(width, height, depth) = utilityFunctions.getBoxSize(box)

	with open('Test1Buildings', 'rb') as hm_file:
	    # Step 3
	    all_buildings = pickle.load(hm_file)

	with open('Test1PathMap', 'rb') as hm_file:
	    # Step 3
	    pathMap = pickle.load(hm_file)

	with open('Test1HeightMap', 'rb') as hm_file:
	    # Step 3
	    height_map = pickle.load(hm_file)

	print("Buildings: ")
	for b in all_buildings:
		print(b.entranceLot)

	# print("Path Map: ")
	# for z in range(depth):
	# 	for x in range(width):
	# 		print(x, z, pathMap[x][z])

	# print("Height Map: ")
	# for z in range(depth):
	# 	for x in range(width):
	# 		print(x, z, height_map[x][z]) 

	vertice1 = all_buildings[0]
	vertice2 = all_buildings[8]

	#path = utilityFunctions.aStar(vertice1.entranceLot, vertice2.entranceLot, pathMap, height_map)
	#print("Result: ")
	#for p in path:
	#	print(p)

	#all_buildings = [all_buildings[0], all_buildings[1], all_buildings[2], all_buildings[3]]

	MST = utilityFunctions.getMST(all_buildings, pathMap, height_map)
	print("Final MST: ")
	for m in MST:
		print(m[0], m[2].entranceLot, m[3].entranceLot)
		print("Path: ")
		if m[1] != None:
			for p in m[1]:
				print(p)


def perform(level, box, options, height_map=None):

	logging.info("BoundingBox coordinates: ({},{}),({},{}),({},{})".format(box.miny, box.maxy, box.minx, box.maxx, box.minz, box.maxz))

	# ==== PREPARATION =====
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	logging.info("Selection box dimensions {}, {}, {}".format(width,height,depth))
	world = utilityFunctions.generateMatrix(level, box, width,depth,height,options)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})

	print(world)

	# calculate height map if not passed as param
	if height_map == None:
		height_map = utilityFunctions.getHeightMap(level,box)
	else:
		logging.info("Skipping height map generation")
	
	# ==== PARTITIONING OF NEIGHBOURHOODS ==== 
	#(center, neighbourhoods) = generateNeighbourhoodPartitioning(world, height_map)

	# ====  GENERATING CITY CENTER ==== 
	all_buildings = []
	# space = utilityFunctions.dotdict({"y_min": center[0], "y_max": center[1], "x_min": center[2], "x_max": center[3], "z_min": center[4], "z_max": center[5]})
	# number_of_tries = 10
	# minimum_h = 3 
	# minimum_w = 25
	# mininum_d = 25

	# minimum_lots = 10
	# available_lots = 0
	# maximum_tries = 200
	# current_try = 0
	# bestPartitioning = []

	# # run the partitioning algorithm for number_of_tries to get different partitionings of the same area
	# logging.info("Generating {} different partitionings for the the City Centre {}".format(number_of_tries, space))
	# partitioning_list = []
	# partitioning = None
	# threshold = 1
	# while available_lots < minimum_lots and current_try < maximum_tries:

	# 	for i in range(number_of_tries):
	# 		#partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [], partition_min=partition_min, valid_min=valid_min)
	# 		partitioning = quadtreeSpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])

	# 		valid_partitioning = []
	# 		for p in partitioning:
	# 			(y_min, y_max, x_min, x_max, z_min, z_max) = (p[0], p[1], p[2],p[3], p[4], p[5])
	# 			failed_conditions = []
	# 			cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
	# 			if cond1 == False: failed_conditions.append(1) #logging.info("Failed Condition 1!")
	# 			cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
	# 			if cond2 == False: failed_conditions.append(2) #logging.info("Failed Condition 2!")
	# 			cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, utilityFunctions.getScoreArea_type1, threshold)
	# 			if cond3 == False: failed_conditions.append(3) #logging.info("Failed Condition 3!")
	# 			if cond1 and cond2 and cond3:
	# 				valid_partitioning.append(p)
	# 			else:
	# 				logging.info("Failed Conditions {}".format(failed_conditions))


	# 		partitioning_list.append((len(valid_partitioning), valid_partitioning))
	# 		logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))

	# 		#valid_partitioning = cleanPartition(partitioning, height_map, minimum_h, minimum_w, mininum_d)
	# 		#partitioning_list.append((len(valid_partitioning), valid_partitioning))
		
	# 	# order partitions by number of valid lots and get the one with the highest
	# 	partitioning_list = sorted(partitioning_list, reverse=True)
	# 	partitioning = partitioning_list[0][1]

	# 	if partitioning_list[0][0] > len(bestPartitioning):
	# 		bestPartitioning = partitioning

	# 	available_lots = len(bestPartitioning)
	# 	logging.info("Current partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

	# 	threshold += 1
	# 	current_try += 1
	
	# logging.info("Final lots ({}) for the City Centre {}: ".format(len(partitioning), space))
	# for p in partitioning:
	# 	logging.info("\t{}".format(p))

	# #return #################

	# for partition in partitioning:
	# 	building = fillBuilding(level, box, matrix, height, width, depth, partition, height_map, options)
	# 	all_buildings.append(building)

	# # ==== GENERATING NEIGHBOURHOODS ==== 
	# for partitioning in neighbourhoods:

	# 	space = utilityFunctions.dotdict({"y_min": partitioning[0], "y_max": partitioning[1], "x_min": partitioning[2], "x_max": partitioning[3], "z_min": partitioning[4], "z_max": partitioning[5]})
	# 	minimum_h = 3 
	# 	minimum_w = 16
	# 	mininum_d = 16

	# 	minimum_lots = 10
	# 	available_lots = 0
	# 	maximum_tries = 200
	# 	current_try = 0
	# 	bestPartitioning = []

	# 	logging.info("Generating {} different partitionings for the neighbourhood {}".format(number_of_tries, space))
	# 	partitioning_list = []
	# 	threshold = 1
	# 	while available_lots < minimum_lots and current_try < maximum_tries:
		
	# 		for i in range(number_of_tries):
	# 			#partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [], partition_min=partition_min, valid_min=valid_min)
	# 			partitioning = quadtreeSpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])

	# 			valid_partitioning = []
	# 			for p in partitioning:
	# 				(y_min, y_max, x_min, x_max, z_min, z_max) = (p[0], p[1], p[2],p[3], p[4], p[5])
	# 				failed_conditions = [] 
	# 				cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
	# 				if cond1 == False: failed_conditions.append(1) #logging.info("Failed Condition 1!")
	# 				cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
	# 				if cond2 == False: failed_conditions.append(2) #logging.info("Failed Condition 2!")
	# 				cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, utilityFunctions.getScoreArea_type1, threshold)
	# 				if cond3 == False: failed_conditions.append(3) #logging.info("Failed Condition 3!")
	# 				if cond1 and cond2 and cond3:
	# 					valid_partitioning.append(p)
	# 					logging.info("Passed the 3 conditions!")
	# 				else:
	# 					logging.info("Failed Conditions {}".format(failed_conditions))

	# 			partitioning_list.append((len(valid_partitioning), valid_partitioning))
	# 			logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))
		
	# 		# order partitions by number of valid lots and get the one with the highest
	# 		partitioning_list = sorted(partitioning_list, reverse=True)
	# 		partitioning = partitioning_list[0][1]

	# 		if partitioning_list[0][0] > len(bestPartitioning):
	# 			bestPartitioning = partitioning

	# 		available_lots = len(bestPartitioning)
	# 		logging.info("Current neighbourhood partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

	# 		threshold += 1
	# 		current_try += 1

	# 		partitioning_list = sorted(partitioning_list, reverse=True)
	# 		partitioning = partitioning_list[0][1]

	# 	logging.info("Final lots ({})for the neighbourhood {}: ".format(len(partitioning), space))
	# 	for p in partitioning:
	# 		logging.info("\t{}".format(p))

	# 	for partition in partitioning:
	# 		house = fillHouse(level, box, matrix, height, width, depth, partition, height_map, options)
	# 		all_buildings.append(house)


	minimum_h = 10 
	minimum_w = 16
	mininum_d = 16

	number_of_tries = 2
	minimum_lots = 100
	available_lots = 0
	maximum_tries = 10
	current_try = 0
	bestPartitioning = []

	logging.info("Generating {} different partitionings for the neighbourhood {}".format(number_of_tries, world_space))
	partitioning_list = []
	threshold = 1
	while available_lots < minimum_lots and current_try < maximum_tries:
	
		for i in range(number_of_tries):
			partitioning = binarySpacePartitioning(world.y_min, world.y_max, world.x_min, world.x_max, world.z_min, world.z_max, [])
			#partitioning = quadtreeSpacePartitioning(world.y_min, world.y_max, world.x_min, world.x_max, world.z_min, world.z_max, [])

			valid_partitioning = []
			for p in partitioning:
				(y_min, y_max, x_min, x_max, z_min, z_max) = (p[0], p[1], p[2],p[3], p[4], p[5])
				failed_conditions = [] 
				cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
				if cond1 == False: failed_conditions.append(1) #logging.info("Failed Condition 1!")
				cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
				if cond2 == False: failed_conditions.append(2) #logging.info("Failed Condition 2!")
				cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, utilityFunctions.getScoreArea_type1, threshold)
				if cond3 == False: failed_conditions.append(3) #logging.info("Failed Condition 3!")
				if cond1 and cond2 and cond3:
					valid_partitioning.append(p)
					logging.info("Passed the 3 conditions!")
				else:
					logging.info("Failed Conditions {}".format(failed_conditions))

			partitioning_list.append((len(valid_partitioning), valid_partitioning))
			logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))
	
		# order partitions by number of valid lots and get the one with the highest
		partitioning_list = sorted(partitioning_list, reverse=True)
		partitioning = partitioning_list[0][1]

		if partitioning_list[0][0] > len(bestPartitioning):
			bestPartitioning = partitioning

		available_lots = len(bestPartitioning)
		logging.info("Current neighbourhood partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

		threshold += 1
		current_try += 1

		partitioning_list = sorted(partitioning_list, reverse=True)
		partitioning = partitioning_list[0][1]

	logging.info("Final lots ({})for the neighbourhood {}: ".format(len(partitioning), world))
	for p in partitioning:
		logging.info("\t{}".format(p))

	for partition in partitioning:
		house = fillHouse(world, height, width, depth, partition, height_map, options)
		all_buildings.append(house)
 
	# ==== GENERATE PATH MAP  ==== 
 	# generate a path map that gives the cost of moving to each neighbouring cell
	pathMap = utilityFunctions.getPathMap(height_map, width, depth)

	#utilityFunctions.saveFiles(height_map, pathMap, all_buildings, "TestMap2HeightMap", "TestMap2PathMap", "TestMap2AllBuildings")

	# # ==== CONNECTING BUILDINGS WITH ROADS  ==== 
	# MST = utilityFunctions.getMST_Manhattan(all_buildings, pathMap, height_map)
	# logging.info("MST result: ")
	# for m in MST:
	# 	logging.info(m)
	
	# pavementBlockID = 4 #171
	# pavementBlockSubtype = 0
	# for m in MST:
	# 	p1 = m[1]
	# 	p2 = m[2]
	# 	logging.info("Pavement with distance {} between {} and {}".format(m[0], p1.entranceLot, p2.entranceLot))
	# 	#path = m[1]

	# 	p1_entrancePoint = p1.entranceLot
	# 	p2_entrancePoint = p2.entranceLot

	#  	path = utilityFunctions.aStar(p1.entranceLot, p2.entranceLot, pathMap, height_map)
	#  	if path != None:
	#  		logging.info("Found path between {} and {}".format(p1.entranceLot, p2.entranceLot))
	# 	 	utilityFunctions.pavementConnection(level, matrix, path, p1, p2, height_map, (pavementBlockID, pavementBlockSubtype))
	# 	else:
	# 		logging.info("Couldnt find path between ", p1.entranceLot, p2.entranceLot)
	#  		utilityFunctions.pavementConnection_old(matrix, p1_entrancePoint[1], p1_entrancePoint[2], p2_entrancePoint[1], p2_entrancePoint[2], height_map, (pavementBlockID, pavementBlockSubtype))
	 	
	# 	#pavementBlockSubtype = (pavementBlockSubtype+1) % 15

	# ==== UPDATE WORLD ==== 
	utilityFunctions.updateWorld(level, box, world, height, width, depth)
	

# ==========================================================================
#				# LOT PREPARING FUNCTIONS
# ==========================================================================

# Perform earthworks on a given lot, returns the height to start construction
def prepareLot(matrix, p, height_map):

	areaScore = utilityFunctions.getScoreArea_type1(height_map, p[2],p[3], p[4], p[5], height_map[p[2]][p[4]])
	logging.info("Preparing lot {} with score {}".format(p, areaScore))

	if areaScore != 0:
		terrain_height = flattenPartition(matrix, p[2],p[3], p[4], p[5], height_map)
		logging.info("Terrain was flattened at height {}".format(terrain_height))
		utilityFunctions.updateHeightMap(height_map, p[2], p[3], p[4], p[5], terrain_height)
		#h = utilityFunctions.convertHeightCoordinates(box, height, terrain_height)
	else:
		heightCounts = utilityFunctions.getHeightCounts(height_map, p[2],p[3], p[4], p[5])
		terrain_height = max(heightCounts, key=heightCounts.get)
		logging.info("No changes in terrain were necessary, terrain at height {}".format(terrain_height))
		utilityFunctions.updateHeightMap(height_map, p[2], p[3], p[4], p[5], terrain_height)
		#h = utilityFunctions.convertHeightCoordinates(box, height, terrain_height)

	h = matrix.getMatrixY(terrain_height)
	logging.info("Index of height {} in selection box matrix: {}".format(terrain_height, h))

	return h

# Given the map matrix, a partition (x_min, x_max, z_min, z_max) and a
# height_map, perform earthworks on this lot by the flattening
# returns the height in which construction should start
def flattenPartition(matrix, x_min, x_max, z_min, z_max, height_map):

	heightCounts = utilityFunctions.getHeightCounts(height_map, x_min, x_max, z_min, z_max)
	most_ocurred_height = max(heightCounts, key=heightCounts.get)

	logging.info("Flattening {}".format(x_min, x_max, z_min, z_max))
	#print("Height Counts: ", heightCounts)
	#print("Most ocurred height: ", most_ocurred_height)

	#box_xmin = utilityFunctions.convertWidthMatrixToBox(box, width, x_min)
	#box_zmin = utilityFunctions.convertDepthMatrixToBox(box, depth, z_min)
	box_xmin = matrix.getWorldX(x_min)
	box_zmin = matrix.getWorldZ(z_min)



	#print("Reconverted coords: ", height_map[x_min][z_min], box_xmin, box_zmin)

	#base_block = level.blockAt(box_xmin, height_map[x_min][z_min], box_zmin)
	#print("Base Block at coords ", x_min, x_max, ": ", base_block)
	base_block = utilityFunctions.getMostOcurredGroundBlock(matrix, height_map, x_min, x_max, z_min, z_max)
	logging.info("Most occurred ground block: {}".format(base_block))
	logging.info("Flattening at height {}".format(most_ocurred_height))

	for x in range(x_min, x_max):
		for z in range(z_min,z_max):
			if height_map[x][z] == most_ocurred_height:
				# Equal height! No flattening needed
				# but lets use the base block just in case
				matrix.setValue(height_map[x][z], x, z, base_block)
				#matrix[height_map[x][z]][x][z] = base_block
			if height_map[x][z] != most_ocurred_height:
				#print(x, z, " Different Height!")

				if height_map[x][z] == -1:
					#print("Position ", x, z, " of height_map is -1. Cannot do earthworks.")
					continue

				#matrix_height = utilityFunctions.convertHeightCoordinates(box, height, height_map[x][z])
				#desired_matrix_height = utilityFunctions.convertHeightCoordinates(box, height, most_ocurred_height)
				matrix_height = matrix.getMatrixY(height_map[x][z])
				desired_matrix_height = matrix.getMatrixY(most_ocurred_height)
				#print("height_map[x][z] = ", height_map[x][z], ", matrix_height = ", matrix_height)
				#print("most_ocurred_height = ", most_ocurred_height, ", desired_matrix_height = ", desired_matrix_height)

				if desired_matrix_height > matrix_height:
					for y in range(matrix_height, desired_matrix_height):
						matrix.setValue(y,x,z, base_block)
						#matrix[y][x][z] = base_block
				else:
					#update every block between top height and the desired height
					# when bringing the ground to a lower level, this will have the 
					# effect of e.g. erasing trees that were on top of that block
					# this may cause some things to be unproperly erased
					# (e.g. a branch of a tree coming from an nearby block)
					# but this is probably the best/less complex solution for this
					for y in range(matrix.height-1, desired_matrix_height):
						matrix.setValue(y,x,z, 0)
						#matrix[y][x][z] = 0
					matrix.setValue(desired_matrix_height,x,z, base_block)
					#matrix[desired_matrix_height][x][z] = base_block

	return most_ocurred_height

# ==========================================================================
#				# PARTITIONING FUNCTIONS
# ==========================================================================

def generateNeighbourhoodPartitioning(space, height_map):
	neighbourhoods = []
	logging.info("Generating Neighbourhood Partitioning...")
	center = utilityFunctions.getSubsection(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.6)
	logging.info("Generated city center: {}".format(center))
	partitions = utilityFunctions.subtractPartition((space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max), center)
	for p in partitions:
		neighbourhoods.append(p)
		logging.info("Generated neighbourhood: {}".format(p))
	return (center, neighbourhoods)

def cleanPartition(partitioning, height_map, minimum_h=4, minimum_w=16, mininum_d=16):
	valid_partitioning = []
	for p in partitioning:
		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map, minimum_h, minimum_w, mininum_d) == True:
			valid_partitioning.append(p)
	return valid_partitioning

# Check if a partition is valid according to some criteria
# Returns false if it does not pass one of the criterion
def isValidPartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map, minimum_h=4, minimum_w=16, mininum_d=16, threshold = 15):

	cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
	#if cond1 == False: print("Failed Condition 1!")
	cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
	#if cond2 == False: print("Failed Condition 2!")
	cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, utilityFunctions.getScoreArea_type1, threshold)
	#if cond3 == False: print("Failed Condition 3!")
		
	return cond1 and cond2 and cond3

def fillBuilding(level, box, matrix, height, width, depth, p, height_map, options):

	#print(p[0],p[1],p[2],p[3], p[4], p[5])	
	#if RNG.random() > 0.5:
	h = prepareLot(matrix, p, height_map)
	building = generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
	constructionArea = building.constructionArea
	utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)
	#utilityFunctions.updateHeightMap(height_map, constructionArea[2], constructionArea[3], constructionArea[4], constructionArea[5], -1)
	return building

def fillHouse(matrix, height, width, depth, p, height_map, options):
	logging.info("Generating a house in lot {}".format(p))
	logging.info("Terrain before flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)
			
	#print(p[0],p[1],p[2],p[3], p[4], p[5])
	#if RNG.random() > 0.5:	
	h = prepareLot(matrix, p, height_map)

	logging.info("Terrain after flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)


	house = generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
	#houses.append(generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options))
	constructionArea = house.constructionArea
	#utilityFunctions.updateHeightMap(height_map, constructionArea[2], constructionArea[3], constructionArea[4], constructionArea[5], -1)
	utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)

	logging.info("Terrain after construction: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)

	return house


# def generatePartitionings(space, partition_min=30, valid_min=15, number_of_tries=10):
# 	logging.info("Generating {} different partitionings for the space {}".format(number_of_tries, space))
# 	partitioning_list = []
# 	for i in range(number_of_tries):
# 		#partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [], partition_min=partition_min, valid_min=valid_min)
# 		partitioning = quadtreeSpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])
# 		partitioning_list.append(partitioning)
# 	return partitioning_list

# def removeInvalidPartitionsFromPartitionings(partitioning_list, height_map, minimum_h=4, minimum_w=16, mininum_d=16):
# 	valid_partitioning_list = []
# 	for partitioning in partitioning_list:
# 		valid_partitioning = cleanPartition(partitioning, height_map, minimum_h, minimum_w, mininum_d)
# 		valid_partitioning_list.append(valid_partitioning)
# 	return valid_partitioning_list

# Gets a list of partitionings and returns the best one 
# based on some criteria (currently the one with highest
# number of valid lots)
# def selectBestPartition(partitioning_list):
# 	partitioning_sizes = []
# 	for partitioning in partitioning_list:
# 		partitioning_sizes.append((len(partitioning), partitioning))
# 	partitioning_list = sorted(partitioning_sizes, reverse=True)
# 	return partitioning_list[0][1]