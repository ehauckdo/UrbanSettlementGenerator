from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
from BinarySpacePartitioning import binarySpacePartitioning

inputs = (
	("House Generator", "label"),
	("Walls", alphaMaterials.Cobblestone),
	("Ceiling", alphaMaterials.WoodPlanks),
	)

def perform(level, box, options):
	#transformBoundingBoxIntoHouse(level,box,options)
	
	multiHouseGenerator(level,box,options)
	#houseGenerator(level,box,options)
	return

def multiHouseGenerator(level,box,options, min_h=8):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)
	
	partitions = binarySpacePartitioning(0, width-1, 0, depth-1, [])
	
	for p in partitions:
		print(p[0],p[1],p[2],p[3])
		h = random.randint(min_h, height)
		if random.random() > 0.5:
			generateHouse(matrix, 0, h-1, p[0],p[1],p[2],p[3], options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] is not 0:
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def houseGenerator(level,box,options, min_h=10, min_w=8, min_d=8):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)

	if height < min_h or width < min_w or depth < min_d:
		return

	h = random.randint(min_h, height)
	w = random.randint(min_w, width)
	d = random.randint(min_d, depth)

	initial_x = (width/2)-(w/2)
	initial_z = (depth/2)-(d/2)

	print("height: "+str(height)+", width: "+str(width)+", depth: "+str(depth))
	print("initial_x: "+str(initial_x)+", initial_z: "+str(initial_z))
	print("h: "+str(h)+", w: "+str(w)+", d: "+str(d))

	generateHouse(matrix, 0, h-1, initial_x, initial_x+w-1, initial_z, initial_z+d-1, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def splitBoundingBox(matrix, x_min, x_max, d_min, d_max):
	pass


def transformBoundingBoxIntoHouse(level,box,options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = generateMatrix(width,depth,height,options)
	matrix = generateHouse(matrix, 0, height-10, 10, width-10, 10, depth-10, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def generateMatrix(width, depth, height, options):
	matrix = [[[(0,0) for z in range(depth)] for x in range(width)] for y in range(height)]		
	return matrix

def generateHouse(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):
	wall = (options["Walls"].ID, 0)
	floor = (options["Walls"].ID, 0)
	ceiling = (options["Ceiling"].ID,0)
	door = (0,0)

	ceiling_bottom = h_max-2 -int((h_max-h_min) * 0.5)

	# generate walls from x_min+1, x_max-1, etc to leave space for the ceiling
	matrix = generateWalls(matrix, h_min, ceiling_bottom, x_min+1, x_max-1, z_min+1, z_max-1, wall)

	matrix = generateFloor(matrix, h_min, x_min+1, x_max-1, z_min+1, z_max-1, floor)

	if random.random() > 0.5:
		matrix = generateCeiling_x(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, 0)
	else:
		matrix = generateCeiling_d(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, 0)

	matrix = addDoor(matrix, x_min+1, x_max-1, z_min+1, z_max-1, h_min+1, ceiling_bottom, door, door)

	
		
	return matrix

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix[h][x][z] = floor

	return matrix

def generateWalls(matrix, h_min, h_max, x_min, x_max, z_min, z_max, wall):

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

def generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, recr):

	# ceiling on every block on uppermost y axis value
	for x in range(x_min+recr, x_max+1-recr):
		for z in range(z_min, z_max+1):
				matrix[h_min+recr][x][z] = ceiling

	if recr < h_max-h_min:
		matrix  = generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, recr+1)

	return matrix

def generateCeiling_d(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, recr):

	# ceiling on every block on uppermost y axis value
	for z in range(z_min+recr, z_max+1-recr):
		for x in range(x_min, x_max+1):
			matrix[h_min+recr][x][z] = ceiling

	if recr < h_max-h_min:
		matrix  = generateCeiling_d(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, recr+1)

	return matrix
def addDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+1][x_min][pos] = door_up
		matrix[h_min][x_min][pos] = door_down
	elif chance < 0.5:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+1][pos][z_min] = door_up
		matrix[h_min][pos][z_min] = door_down
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+1][x_min-1][pos] = door_up
		matrix[h_min][x_min-1][pos] = door_down
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+1][pos][z_min-1] = door_up
		matrix[h_min][pos][z_min-1] = door_down

	return matrix