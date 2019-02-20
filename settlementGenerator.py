from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
from BinarySpacePartitioning import binarySpacePartitioning
from HouseGenerator import houseGenerator, generateHouse
from MultistoreyBuildingGenerator import buildingGenerator, generateBuilding, generateHospital

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
	#settlementGenerator(level,box,options)

	findTerrain(level,box,options)
	#hospitalSettlementGenerator(level,box,options)
	#houseGenerator(level,box,options)
	#buildingGenerator(level,box,options)
	return

def findTerrain(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	terrain = [[0 for z in range(box.minz,box.maxz)] for x in range(box.minx,box.maxx)]
	
	# generated matrix
	for x in range(0, box.maxx-box.minx):
		print(terrain[x])

	for d, z in zip(range(box.minz,box.maxz), range(0, box.maxz-box.minz)):
		for w, x in zip(range(box.minx,box.maxx), range(0, box.maxx-box.minx)):
			terrain[x][z] = utilityFunctions.findTerrain(level, w, d, box.miny, box.maxy)
	print("")

	# filled matrix
	for x in range(0, box.maxx-box.minx):
		print(terrain[x])

	validAreas = []

	for i in range(0, 100):
		random_x = random.randint(0, box.maxx-box.minx)
		random_z = random.randint(0,box.maxz-box.minz)
		if checkSameHeight(terrain, 0, box.maxx-box.minx, 0,box.maxz-box.minz, random_x, random_z, 10, 10):
			print(random_x, random_z, "Valid area!!")
			newValidArea = (random_x, random_x+10, random_z, random_z+10)
			if newValidArea not in validAreas:
				validAreas.append(newValidArea)
		else:
			print(random_x, random_z, "Invalid area")

	print("Valid areas found:")
	for a in validAreas:
		print(a)

	print("Original matrix:")
	printMatrix(matrix, height,width,depth)

	for a in validAreas:
		min_h = terrain[a[0]][a[2]]
		print("INSERTING AREA ", a, ", at height: ", min_h)
		print("Converting box height to matrix height: ")
		matrix_height = convertHeightCoordinates(level,box,matrix,height, min_h)
		print("Converted height: ", matrix_height, height)
		generateHouse(matrix, matrix_height, height, a[0],a[1],a[2],a[3], options)
		print("New matrix: ")
		printMatrix(matrix, height, width, depth)
		break

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

	# for d, z in zip(range(box.minz,box.maxz), range(0, box.maxz-box.minz)):
	# 	level_layout = ""
	# 	for w, x in zip(range(box.minx,box.maxx), range(0, box.maxx-box.minx)):
	# 		level_layout += str(utilityFunctions.findTerrain(level, w, d, box.miny, box.maxy))+" "
	# 		#print(level.blockAt(x,y,z))
	# 	print(level_layout)
	# print("")

def printMatrix(matrix, height, width, depth):
	for h in range(0,height):
		print("matrix at height: ", h)
		for x in range(0,width):
			print(matrix[h][x])
	
def checkSameHeight(terrain, minx, maxx, minz, maxz, random_x, random_z, mininum_w, mininum_d):
	# sample testing
	print("Testing if valid area starting in ", random_x, random_z)
	print("limits of matrix: ", minx, maxx, minz, maxz)

	if random_x + mininum_w > maxx or random_z + mininum_d > maxz:
		return False

	initial_value = terrain[random_x][random_z]

	for x in range(random_x, random_x + mininum_w):
		for z in range(random_z, random_z + mininum_d):
			print("Checking x, z: ", x, z)
			if terrain[x][z] != initial_value:
				return False

	return True

def convertHeightCoordinates(level, box, matrix, max_h, height):
	for y, h in zip(range(box.miny,box.maxy), range(0,max_h)):
		if y == height:
			return h

def removeOverlaping(areas):
	#for index, area1 in enumerate(areas);
		# remove overlaping partitions here!!
	pass

def pavementGround(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	for x in range(0,width):
		for z in range(0,depth):
			matrix[0][x][z] = (1,0)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def settlementGenerator(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)
	
	partitions = binarySpacePartitioning(0, width-1, 0, depth-1, [])

	p = utilityFunctions.getBiggestPartition(partitions)
	generateBuilding(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)
	partitions.remove(p)

	for p in partitions:
		print(p[0],p[1],p[2],p[3])
		
		if random.random() > 0.5:
			if random.random() > 0.8:
				generateHouse(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)
				#generateBuilding(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)
			else:
				#p = utilityFunctions.getSubsection(p[0],p[1],p[2],p[3], 0.5)
				generateHouse(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)


def hospitalSettlementGenerator(level,box,options):

	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	hospitalPartition = utilityFunctions.getSubsection(0, width-1, 0, depth-1, 0.4)
	neighbourhoods = utilityFunctions.subtractPartition((0, width-1, 0, depth-1), hospitalPartition)

	hp = hospitalPartition
	hospitalPartition = utilityFunctions.getSubsection(hp[0], hp[1], hp[2], hp[3], 0.8)


	generateHospital(matrix, 0, height-1, hospitalPartition[0]+10, hospitalPartition[1]-10,hospitalPartition[2]+10,hospitalPartition[3]-10, options)

	for n in neighbourhoods:
		partitions = binarySpacePartitioning(n[0], n[1], n[2], n[3], [])

		for p in partitions:
		# 	getEuclidianDistancePartitions(p1, p2):

			if random.random() > 0.5:
				generateHouse(matrix, 0, height-1, p[0],p[1],p[2],p[3], options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

