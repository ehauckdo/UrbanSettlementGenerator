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
	#findTerrain(level,box,options)
	mainGenerator(level,box,options)
	#hospitalSettlementGenerator(level,box,options)
	#houseGenerator(level,box,options)
	#buildingGenerator(level,box,options)

def mainGenerator(level,box,options):
	height_map = utilityFunctions.getHeightMap(level,box)
	validAreas = utilityFunctions.getAreasSameHeight(box, height_map)
	fillAreas(level,box,options, validAreas, height_map)

def fillAreas(level,box,options,validAreas,terrain):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	for a in validAreas:
		min_h = terrain[a[0]][a[2]]
		matrix_height = convertHeightCoordinates(box,height, min_h)
		print("INSERTING AREA ", a, ", between heights: ", matrix_height, height)
		generateHouse(matrix, matrix_height, height, a[0],a[1],a[2],a[3], options)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)
	
def convertHeightCoordinates(box,max_h, height):
	print("Height: ", height)
	for y, h in zip(range(box.miny,box.maxy), range(0,max_h)):
		print(y, h)
		if y == height:
			return h

def pavementGround(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	for x in range(0,width):
		for z in range(0,depth):
			matrix[0][x][z] = (1,0)

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

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

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)


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

	utilityFunctions.updateWorld(level, box, matrix, height, width, depth)

