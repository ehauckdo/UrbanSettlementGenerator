from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
import pickle
import RNG
import logging
from SpacePartitioning import binarySpacePartitioning, quadtreeSpacePartitioning
import HouseGenerator 
import MultistoreyBuildingGenerator
from Earthworks import prepareLot

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
	world = utilityFunctions.generateMatrix(level, box, width,depth,height)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})

	print(world)

	# calculate height map if not passed as param
	if height_map == None:
		height_map = utilityFunctions.getHeightMap(level,box)
	else:
		logging.info("Skipping height map generation")
	
	# ==== PARTITIONING OF NEIGHBOURHOODS ==== 
	(center, neighbourhoods) = generateNeighbourhoodPartitioning(world_space, height_map)

	# ====  GENERATING CITY CENTER ==== 
	all_buildings = []
	# space = utilityFunctions.dotdict({"y_min": center[0], "y_max": center[1], "x_min": center[2], "x_max": center[3], "z_min": center[4], "z_max": center[5]})
	number_of_tries = 10
	minimum_h = 3 
	minimum_w = 25
	mininum_d = 25

	minimum_lots = 10
	available_lots = 0
	maximum_tries = 50
	current_try = 0
	bestPartitioning = []

	# run the partitioning algorithm for number_of_tries to get different partitionings of the same area
	logging.info("Generating {} different partitionings for the the City Centre {}".format(number_of_tries, center))
	partitioning_list = []
	partitioning = None
	threshold = 1
	while available_lots < minimum_lots and current_try < maximum_tries:

		for i in range(number_of_tries):
			partitioning = binarySpacePartitioning(center[0], center[1], center[2], center[3], center[4], center[5], [])
			#partitioning = quadtreeSpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])

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
				else:
					logging.info("Failed Conditions {}".format(failed_conditions))


			partitioning_list.append((len(valid_partitioning), valid_partitioning))
			logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))

			#valid_partitioning = cleanPartition(partitioning, height_map, minimum_h, minimum_w, mininum_d)
			#partitioning_list.append((len(valid_partitioning), valid_partitioning))
		
		# order partitions by number of valid lots and get the one with the highest
		partitioning_list = sorted(partitioning_list, reverse=True)
		partitioning = partitioning_list[0][1]

		if partitioning_list[0][0] > len(bestPartitioning):
			bestPartitioning = partitioning

		available_lots = len(bestPartitioning)
		logging.info("Current partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

		threshold += 1
		current_try += 1
	
	logging.info("Final lots ({}) for the City Centre {}: ".format(len(partitioning), center))
	for p in partitioning:
		logging.info("\t{}".format(p))

	for partition in partitioning:
		building = generateBuilding(world, partition, height_map)
		all_buildings.append(building)

	# # ==== GENERATING NEIGHBOURHOODS ==== 
	for partitioning in neighbourhoods:

		space = utilityFunctions.dotdict({"y_min": partitioning[0], "y_max": partitioning[1], "x_min": partitioning[2], "x_max": partitioning[3], "z_min": partitioning[4], "z_max": partitioning[5]})
		minimum_h = 3 
		minimum_w = 16
		mininum_d = 16

		minimum_lots = 10
		available_lots = 0
		maximum_tries = 50
		current_try = 0
		bestPartitioning = []

		logging.info("Generating {} different partitionings for the neighbourhood {}".format(number_of_tries, space))
		partitioning_list = []
		threshold = 1
		while available_lots < minimum_lots and current_try < maximum_tries:
		
			for i in range(number_of_tries):
				partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])
				#partitioning = quadtreeSpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])

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

		logging.info("Final lots ({})for the neighbourhood {}: ".format(len(partitioning), space))
		for p in partitioning:
			logging.info("\t{}".format(p))

		for partition in partitioning:
			house = generateHouse(world, partition, height_map)
			all_buildings.append(house)


	############# START TESTING SECTION ###############

	# minimum_h = 3 
	# minimum_w = 16
	# mininum_d = 16

	# number_of_tries = 10
	# minimum_lots = 100
	# available_lots = 0
	# maximum_tries = 100
	# current_try = 0
	# bestPartitioning = []

	# logging.info("Generating {} different partitionings for the neighbourhood {}".format(number_of_tries, world_space))
	# partitioning_list = []
	# threshold = 1
	# while available_lots < minimum_lots and current_try < maximum_tries:
	
	# 	for i in range(number_of_tries):
	# 		partitioning = binarySpacePartitioning(0, height-1, 0, width-1, 0, depth-1, [])
	# 		#partitioning = quadtreeSpacePartitioning(world.y_min, world.y_max, world.x_min, world.x_max, world.z_min, world.z_max, [])

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
	# 				logging.info("Passed the 3 conditions!")
	# 			else:
	# 				logging.info("Failed Conditions {}".format(failed_conditions))

	# 		partitioning_list.append((len(valid_partitioning), valid_partitioning))
	# 		logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))
	
	# 	# order partitions by number of valid lots and get the one with the highest
	# 	partitioning_list = sorted(partitioning_list, reverse=True)
	# 	partitioning = partitioning_list[0][1]

	# 	if partitioning_list[0][0] > len(bestPartitioning):
	# 		bestPartitioning = partitioning

	# 	available_lots = len(bestPartitioning)
	# 	logging.info("Current neighbourhood partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

	# 	threshold += 1
	# 	current_try += 1

	# 	partitioning_list = sorted(partitioning_list, reverse=True)
	# 	partitioning = partitioning_list[0][1]

	# logging.info("Final lots ({})for the neighbourhood {}: ".format(len(partitioning), world))
	# for p in partitioning:
	# 	logging.info("\t{}".format(p))

	# for partition in partitioning:
	# 	house = generateHouse(world, partition, height_map)
	# 	all_buildings.append(house)

	############# END TESTING SECTION ###############
 
	# ==== GENERATE PATH MAP  ==== 
 	# generate a path map that gives the cost of moving to each neighbouring cell
	pathMap = utilityFunctions.getPathMap(height_map, width, depth)

	#utilityFunctions.saveFiles(height_map, pathMap, all_buildings, "TestMap2HeightMap", "TestMap2PathMap", "TestMap2AllBuildings")

	# ==== CONNECTING BUILDINGS WITH ROADS  ==== 
	# logging.info("Calling MST on {} buildings".format(len(all_buildings)))
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
	#  		logging.info("Found path between {} and {}. Generating road...".format(p1.entranceLot, p2.entranceLot))
	# 	 	utilityFunctions.pavementConnection(world, path, height_map, (pavementBlockID, pavementBlockSubtype))
	# 	else:
	# 		logging.info("Couldnt find path between {} and {}. Generating a straight road between them...".format(p1.entranceLot, p2.entranceLot))
	#  		utilityFunctions.pavementConnection_old(world, p1_entrancePoint[1], p1_entrancePoint[2], p2_entrancePoint[1], p2_entrancePoint[2], height_map, (pavementBlockID, pavementBlockSubtype))
	 	
	# 	#pavementBlockSubtype = (pavementBlockSubtype+1) % 15

	# ==== UPDATE WORLD ==== 
	#utilityFunctions.updateWorld(level, box, world, height, width, depth)
	world.updateWorld()
	

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

def generateBuilding(matrix, p, height_map):

	h = prepareLot(matrix, p, height_map)
	building = MultistoreyBuildingGenerator.generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5])
	constructionArea = building.constructionArea
	utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)
	#utilityFunctions.updateHeightMap(height_map, constructionArea[2], constructionArea[3], constructionArea[4], constructionArea[5], -1)
	return building

def generateHouse(matrix, p, height_map):
	logging.info("Generating a house in lot {}".format(p))
	logging.info("Terrain before flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)
				
	h = prepareLot(matrix, p, height_map)

	logging.info("Terrain after flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)


	house = HouseGenerator.generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5])
	
	utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)

	logging.info("Terrain after construction: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)

	return house

