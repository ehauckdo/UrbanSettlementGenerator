from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
from SpacePartitioning import binarySpacePartitioning, quadtreeSpacePartitioning
from HouseGenerator import generateHouse
from MultistoreyBuildingGenerator import generateBuilding, generateHospital
import pickle
import RNG

inputs = (
	("House Generator", "label"),
	("Walls Material Type", alphaMaterials.DoubleStoneSlab),
	("Walls Material Subtype (min)", 11),
	("Walls Material Subtype (max)", 15),
	("Ceiling Material Type", alphaMaterials.WoodPlanks),
	("Ceiling Material Subtype (min)", 1),
	("Ceiling Material Subtype (max)", 5)
	)

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

	# PREPARATION
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})

	# calculate height map if not passed as param
	if height_map == None:
		height_map = utilityFunctions.getHeightMap(level,box)

	
	# print("Path Map: ")
	# for z in range(depth):
	# 	for x in range(width):
	# 		print(x, z, pathMap[x][z])
	
	# PARTITIONING OF NEIGHBOURHOODS
	(center, neighbourhoods) = generateNeighbourhoodPartitioning(world_space, height_map)

	# GENERATING CITY CENTER
	all_buildings = []
	space = utilityFunctions.dotdict({"y_min": center[0], "y_max": center[1], "x_min": center[2], "x_max": center[3], "z_min": center[4], "z_max": center[5]})
	print("City Center Space: ")
	print(space)
	partitioning_list = generatePartitionings(space, 35, 20)
	partitioning_list = removeInvalidPartitionsFromPartitionings(partitioning_list, height_map, 3, 25, 25)
	partitioning = selectBestPartition(partitioning_list)
	print("City Center: ")
	for p in partitioning:
		print (p)
	buildings = fillBuildings(level, box, matrix, height, width, depth, partitioning, height_map, options)
	all_buildings.extend(buildings)
	

	# GENERATING NEIGHBOURHOODS
	for partitioning in neighbourhoods:
		continue

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
 
 	# generate a path map that gives the cost of moving to each neighbouring cell
	pathMap = utilityFunctions.getPathMap(height_map, width, depth)

	#for x, w in zip(range(box.minx,box.maxx), range(0,width)):
	#	for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
	#		if height_map[w][d] == -1:
	#				matrix[100][w][d] = (168, 0)

	#with open('Test1HeightMap', 'wb') as matrix_file:
 	#	pickle.dump(height_map, matrix_file)

 	#with open('Test1PathMap', 'wb') as matrix_file:
 	#	pickle.dump(pathMap, matrix_file)

	#with open('Test1Buildings', 'wb') as matrix_file:
	#	pickle.dump(all_buildings, matrix_file)

	MST = utilityFunctions.getMST_Manhattan(all_buildings, pathMap, height_map)
	print("Final MST: ")
	for m in MST:
		print(m)
	
	pavementBlockID = 171
	pavementBlockSubtype = 0
	for m in MST:
		#print("Pavement with distance ", m[0], "between ", m[2].entranceLot, m[3].entranceLot)
		#path = m[1]
	 	p1 = m[1]
	 	p2 = m[2]

	 	p1_entrancePoint = p1.entranceLot
	 	p2_entrancePoint = p2.entranceLot

	 	#path = utilityFunctions.aStar(p1.entranceLot, p2.entranceLot, pathMap, height_map)
	 	#if path != None:
	 	#	print("Found path between ", p1.entranceLot, p2.entranceLot)
		# 	utilityFunctions.pavementConnection(matrix, path, p1, p2, height_map, (pavementBlockID, pavementBlockSubtype))
		#else:
		#	print("Couldnt find path between ", p1.entranceLot, p2.entranceLot)
	 	#	utilityFunctions.pavementConnection_old(matrix, p1_entrancePoint[1], p1_entrancePoint[2], p2_entrancePoint[1], p2_entrancePoint[2], height_map, (pavementBlockID, pavementBlockSubtype))
	 	#
	 	pavementBlockSubtype = (pavementBlockSubtype+1) % 15
	 	print("Block Subtype: ", pavementBlockSubtype)

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
	print("Base Block at coords ", x_min, x_max, ": ", base_block)
	base_block = utilityFunctions.getMostOcurredGroundBlock(level, height_map, x_min, x_max, z_min, z_max)

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
		#partitioning = binarySpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [], partition_min=partition_min, valid_min=valid_min)
		partitioning = quadtreeSpacePartitioning(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, [])
		partitioning_list.append(partitioning)
	return partitioning_list

def generateNeighbourhoodPartitioning(space, height_map):
	neighbourhoods = []
	center = utilityFunctions.getSubsection(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.8)
	partitions = utilityFunctions.subtractPartition((space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max), center)
	for p in partitions:
		neighbourhoods.append(p)
	return (center, neighbourhoods)

def removeInvalidPartitionsFromPartitionings(partitioning_list, height_map, minimum_h=4, minimum_w=16, mininum_d=16):
	valid_partitioning_list = []
	for partitioning in partitioning_list:
		valid_partitioning = cleanPartition(partitioning, height_map, minimum_h, minimum_w, mininum_d)
		valid_partitioning_list.append(valid_partitioning)
	return valid_partitioning_list

def cleanPartition(partitioning, height_map, minimum_h=4, minimum_w=16, mininum_d=16):
	valid_partitioning = []
	for p in partitioning:
		if isValidPartition(p[0], p[1], p[2], p[3], p[4], p[5], height_map, minimum_h, minimum_w, mininum_d) == True:
			valid_partitioning.append(p)
	return valid_partitioning

# Check if a partition is valid according to some criteria
# Returns false if it does not pass one of the criterion
def isValidPartition(y_min, y_max, x_min, x_max, z_min, z_max, height_map, minimum_h=4, minimum_w=16, mininum_d=16, threshold = 5):

	cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
	#if cond1 == False: print("Failed Condition 1!")
	cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
	#if cond2 == False: print("Failed Condition 2!")
	cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, utilityFunctions.getScoreArea_type1, threshold)
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
		
		#if RNG.random() > 0.5:
		if RNG.random() > 0.8:
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
		#if RNG.random() > 0.5:
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		building = generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5], options)
		buildings.append(building)
		constructionArea = building.constructionArea
		utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)
		#utilityFunctions.updateHeightMap(height_map, constructionArea[2], constructionArea[3], constructionArea[4], constructionArea[5], -1)
	return buildings

def fillHouses(level, box, matrix, height, width, depth, partitioning, height_map, options):
	ceilingBlockID = 35
	ceilingBlockSubtype = RNG.randint(0, 14)
	houses = []
	for p in partitioning:
		print("Height map before update in building ", p)
		for x in range (p[2], p[3]):
			line = ""
			for z in range(p[4], p[5]):
				line += str(height_map[x][z])+" "
			print(line)
				
		#print(p[0],p[1],p[2],p[3], p[4], p[5])
		#if RNG.random() > 0.5:	
		h = prepareLot(level, box, matrix, height, width, depth, p, height_map)
		house = generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options, (ceilingBlockID, ceilingBlockSubtype))
		houses.append(house)
		#houses.append(generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5], options))
		constructionArea = house.constructionArea
		#utilityFunctions.updateHeightMap(height_map, constructionArea[2], constructionArea[3], constructionArea[4], constructionArea[5], -1)
		utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)
		#for x in range(p[2]+1, p[3]-1):
		#	for z in range(p[3]-1, p[4]+1):
		#		height_map[x][z] = -1


		print("Updated height map!", p)
		for x in range (p[2], p[3]):
			line = ""
			for z in range(p[4], p[5]):
				line += str(height_map[x][z])+" "
			print(line)
	return houses

