from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random

inputs = (
	("House Generator", "label"),
	("Walls", alphaMaterials.Cobblestone),
	("Ceiling", alphaMaterials.WoodPlanks),
	)

def perform(level, box, options):
	#houseGenerator(level,box,options)
	mazeGenerator(level,box,options)
	return

def mazeGenerator(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)

	initial_x = random.randint(1, width-15)
	initial_z = random.randint(1, depth-15)

	w = random.randint(6, 15)
	d = random.randint(6, 15)
	h = random.randint(12, height-1)

	generateHouse(matrix, 0, h, initial_x, initial_x+w, initial_z, initial_z+d, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] is not 0:
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def houseGenerator(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)
	matrix = generateHouse(matrix, 0, height-10, 10, width-10, 10, depth-10, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] is not 0:
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def generateMatrix(width, depth, height, options):
	matrix = [[[(0,0) for z in range(depth)] for x in range(width)] for y in range(height)]		
	return matrix

def generateHouse(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):
	wall = (options["Walls"].ID, 0)
	ceiling = (options["Ceiling"].ID,0)
	door = (0,0)

	ceiling_bottom = h_max-2 -int((h_max-h_min) * 0.5)

	matrix = addWalls(matrix, h_min, ceiling_bottom, x_min, x_max, z_min, z_max, wall)

	#matrix = addCeiling(matrix, h_max-h_min+1, x_min, x_max, z_min, z_max, ceiling)
	matrix = generateCeiling(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, 0)
		
	matrix = addDoor(matrix, x_min, x_max, z_min, z_max, h_min, ceiling_bottom, door, door)
		
	return matrix

def addWalls(matrix, h_min, h_max, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, h_max):
			matrix[y][x][z_max] = wall
			matrix[y][x][z_min] = wall

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, h_max):
			matrix[y][x_max][z] = wall
			matrix[y][x_min][z] = wall

	return matrix

def addCeiling(matrix, height, x_min, x_max, z_min, z_max, ceiling):

	# ceiling on every block on uppermost y axis value
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
				matrix[height-1][x][z] = ceiling

	return matrix

def generateCeiling(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, recr):

	# ceiling on every block on uppermost y axis value
	for x in range(x_min+recr-1, x_max+2-recr):
		for z in range(z_min-1, z_max+2):
				matrix[h_min+recr][x][z] = ceiling

	if recr < h_max-h_min:
		matrix  = generateCeiling(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, recr+1)

	return matrix

def addDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(z_min+1,z_max-1)
		matrix[1][x_min][pos] = door_up
		matrix[0][x_min][pos] = door_down
	elif chance < 0.5:
		pos = random.randint(x_min+1,x_max-1)
		matrix[1][pos][z_min] = door_up
		matrix[0][pos][z_min] = door_down
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[1][x_min-1][pos] = door_up
		matrix[0][x_min-1][pos] = door_down
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[1][pos][z_min-1] = door_up
		matrix[0][pos][z_min-1] = door_down

	return matrix