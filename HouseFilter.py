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
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)


def generateMatrix(width, depth, height, options):
	matrix = [[[(0,0) for z in range(depth)] for x in range(width)] for y in range(height)]

	wall = (options["Walls"].ID, 0)
	ceiling = (options["Ceiling"].ID,0)
	door = (0,0)

	matrix = addWalls(matrix, 0, height, 0, width, 0, depth, wall)

	matrix = addCeiling(matrix, height, 0, width, 0, depth, ceiling)
		
	matrix = addDoor(matrix, width, depth, height, door, door)
		
	return matrix

def addWalls(matrix, h_min, h_max, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max):
		for y in range(h_min, h_max):
			matrix[y][x][0] = wall
			matrix[y][x][z_max-z_min-1] = wall

	# walls along z axis
	for z in range(z_min, z_max):
		for y in range(h_min, h_max):
			matrix[y][0][z] = wall
			matrix[y][x_max-x_min-1][z] = wall

	return matrix

def addCeiling(matrix, height, x_min, x_max, z_min, z_max, ceiling):

	# ceiling on every block on uppermost y axis value
	for x in range(x_min, x_max):
		for z in range(z_min, z_max):
				matrix[height-1][x][z] = ceiling

	return matrix

def addDoor(matrix, width, depth, height, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(1,depth-2)
		matrix[1][0][pos] = door_up
		matrix[0][0][pos] = door_down
	elif chance < 0.5:
		pos = random.randint(1,width-2)
		matrix[1][pos][0] = door_up
		matrix[0][pos][0] = door_down
	elif chance < 0.75:
		pos = random.randint(1,depth-2)
		matrix[1][width-1][pos] = door_up
		matrix[0][width-1][pos] = door_down
	else:
		pos = random.randint(1,width-2)
		matrix[1][pos][depth-1] = door_up
		matrix[0][pos][depth-1] = door_down

	return matrix