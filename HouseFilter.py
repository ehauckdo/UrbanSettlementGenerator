from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random

inputs = (
	("House Generator", "label"),
	("Walls", alphaMaterials.Cobblestone),
	("Ceiling", alphaMaterials.WoodPlanks),
	)

def perform(level, box, options):
	generateHouse(level,box,options)
	return

def generateHouse(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)

	zip(range(box.miny,box.maxy), range(0,height))

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] is not 0:
					utilityFunctions.setBlock(level, (matrix[h][w][d], 0), x, y, z)


def generateMatrix(width, depth, height, options):
	matrix = [[[options["Walls"].ID for z in range(depth)] for x in range(width)] for y in range(height)]

	for x in range(len(matrix[height-1])):
		for z in range(len(matrix[height-1][x])):
				matrix[height-1][x][z] = options["Ceiling"].ID

	return matrix
