from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
from BinarySpacePartitioning import binarySpacePartitioning
from HouseGenerator import houseGenerator
from MultistoreyBuildingGenerator import buildingGenerator

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
	settlementGenerator(level,box,options)
	#houseGenerator(level,box,options)
	#buildingGenerator(level,box,options)
	return

def pavementGround(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)

	for x in range(0,width):
		for z in range(0,depth):
			matrix[0][x][z] = (1,0)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def settlementGenerator(level,box,options, min_h=10):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)

	min_h = height - int(height*0.2)
	
	partitions = binarySpacePartitioning(0, width-1, 0, depth-1, [])
	
	for p in partitions:
		print(p[0],p[1],p[2],p[3])
		h = random.randint(min_h, height)
		if random.random() > 0.5:
			generateHouse(matrix, 0, h-1, p[0],p[1],p[2],p[3], options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)


