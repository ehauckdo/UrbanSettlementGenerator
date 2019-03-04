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

def perform(level, box, options):
	
	#pavementGround(level,box,options)
	#findTerrain(level,box,options)
	#mainGenerator(level,box,options)

	
	#hospitalSettlementGenerator(level,box,options)
	#houseGenerator(level,box,options)
	#buildingGenerator(level,box,options)

	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	height_map = utilityFunctions.getHeightMap(level,box)

	#print("BOX: ")
	#print(box.minx, box.maxx, box.minx,box.maxx, box.minz,box.maxz)
	#print(box.__dict__)
	#for y in range(box.miny,box.maxy):
	#	for x in range(box.minx,box.maxx):
	#		for z in range(box.minz,box.maxz):
	#			print("Block at :", y, x, z, " = ", level.blockAt(x, y, z), type(level.blockAt(x, y, z)))
	#			pass
	
	#flattenPartition_prototype(matrix, level, box, height, width, depth, box.miny, box.maxy, box.minx, box.maxx, box.minz,box.maxz, height_map)

	settlementGenerator(level,box, matrix, height, width, depth, height_map, options)

	#hospitalSettlementGenerator(level, box, matrix, height, width, depth, height_map, options)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

def preparePartition(level, box, matrix, height, width, depth, p, height_map):
	areaScore = utilityFunctions.getScoreArea(height_map, p[0], p[1], p[2], p[3], height_map[p[0]][p[2]])
	print("Area score: ", areaScore)

	if areaScore != 0:
		flattened_height = flattenPartition(matrix, level, box, height, width, depth, p[0], p[1], p[2], p[3], height_map)
		print("Flattened height: ", flattened_height)
		h = utilityFunctions.convertHeightCoordinates(box, height, flattened_height)
	else:
		heightCounts = utilityFunctions.getHeightCounts(height_map, p[0], p[1], p[2], p[3])
		most_ocurred_height = max(heightCounts, key=heightCounts.get)
		print("Non flattened height: ", most_ocurred_height)
		h = utilityFunctions.convertHeightCoordinates(box, height, most_ocurred_height)

	return h

def flattenPartition(matrix, level, box, height, width, depth, x_min, x_max, z_min, z_max, height_map):

	heightCounts = utilityFunctions.getHeightCounts(height_map, x_min, x_max, z_min, z_max)
	most_ocurred_height = max(heightCounts, key=heightCounts.get)

	print("Height Counts: ", heightCounts)
	print("Most ocurred height: ", most_ocurred_height)

	box_xmin = utilityFunctions.convertWidthMatrixToBox(box, width, x_min)
	box_zmin = utilityFunctions.convertDepthMatrixToBox(box, depth, z_min)
	print("Reconverted coords: ", height_map[x_min][z_min], box_xmin, box_zmin)

	base_block = level.blockAt(box_xmin, height_map[x_min][z_min], box_zmin)
	print("Base Block at coords ", x_min, x_max, ": ", base_block)

	for x in range(x_min, x_max):
		for z in range(z_min,z_max):
			if height_map[x][z] == most_ocurred_height:
				# Equal height! No flattening needed
				pass
			if height_map[x][z] != most_ocurred_height:
				print(x, z, " Different Height!")

				if height_map[x][z] == -1:
					print("Position ", x, z, " of height_map is -1. Cannot do earthworks.")
					continue

				matrix_height = utilityFunctions.convertHeightCoordinates(box, height, height_map[x][z])
				desired_matrix_height = utilityFunctions.convertHeightCoordinates(box, height, most_ocurred_height)
				print("height_map[x][z] = ", height_map[x][z], ", matrix_height = ", matrix_height)
				print("most_ocurred_height = ", most_ocurred_height, ", desired_matrix_height = ", desired_matrix_height)

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

def fillAreas(level,box,options,validAreas,terrain):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	for a in validAreas:
		min_h = terrain[a[0]][a[2]]
		matrix_height = utilityFunctions.convertHeightCoordinates(box,height, min_h)
		#utilityFunctions.printMatrix(matrix, height, width, depth)
		print("INSERTING AREA ", a, ", between heights: ", matrix_height, height)
		generateHouse(matrix, matrix_height, height, a[0],a[1],a[2],a[3], options)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)
	

def pavementGround(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	for x in range(0,width):
		for z in range(0,depth):
			matrix[0][x][z] = (1,0)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

def settlementGenerator(level,box,matrix, height, width, depth, height_map, options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	
	partitions = binarySpacePartitioning(0, width-1, 0, depth-1, [])

	#p = utilityFunctions.getBiggestPartition(partitions)
	#generateBuilding(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)
	#partitions.remove(p)

	for p in partitions:
		print(p[0],p[1],p[2],p[3])
		
		if random.random() > 0.5:
			if random.random() > 0.8:
				#generateHouse(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)
				h = preparePartition(level, box, matrix, height, width, depth, p, height_map)
				generateBuilding(matrix, h, height-1, p[0],p[1],p[2],p[3], options)
			else:
				#p = utilityFunctions.getSubsection(p[0],p[1],p[2],p[3], 0.5)
				h = preparePartition(level, box, matrix, height, width, depth, p, height_map)
				generateHouse(matrix, h, height-1, p[0],p[1],p[2],p[3], options)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

def hospitalSettlementGenerator(level, box, matrix, height, width, depth, height_map, options):

	partitions = hospitalSettlementGeneratePartitioning(height,width,depth)
	for p in partitions:
		print(p)

	hp = partitions[0]
	h = preparePartition(level, box, matrix, height, width, depth, hp, height_map)

	generateHospital(matrix, h, height-1, hp[0], hp[1],hp[2],hp[3], options)

	for i in range(1, len(partitions)):
		p = partitions[i]
		#if random.random() > 0.5:
		print("Building on partition ", p)
		h = preparePartition(level, box, matrix, height, width, depth, p, height_map)
		generateHouse(matrix, h, height-1, p[0],p[1],p[2],p[3], options)

	return matrix

def hospitalSettlementGeneratePartitioning(height, width, depth):

	partitions = []

	hospitalPartition = utilityFunctions.getSubsection(0, width-1, 0, depth-1, 0.4)
	partitions.append(hospitalPartition)

	neighbourhoods = utilityFunctions.subtractPartition((0, width-1, 0, depth-1), hospitalPartition)
	for n in neighbourhoods:
		neighbourhood_partitioning = binarySpacePartitioning(n[0], n[1], n[2], n[3], [])
		for p in neighbourhood_partitioning:
			partitions.append(p)

	return partitions


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