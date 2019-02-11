from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math

def generateMatrix(width, depth, height, options):
	matrix = [[[(0,0) for z in range(depth)] for x in range(width)] for y in range(height)]		
	return matrix

def buildingGenerator(level,box,options, min_h=20, min_w=8, min_d=8):
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

	#generateHouse(matrix, 0, h-1, initial_x, initial_x+w-1, initial_z, initial_z+d-1, options)
	matrix = generateBuilding(matrix, 0, height-1, 0, width-1, 0, depth-1, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)


def generateBuilding(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):

	wall = (43,14)
	ceiling = (43,14)
	floor = wall
	door = (0,0)

	floor_size = 8
	while (h_max-h_min) % floor_size != 0:
		h_max -= 1

	matrix = generateBuildingWalls(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)
	matrix = generateBuildingWindows(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max)
	# fix this h_min+1 thing, check how it's working for regular houses
	matrix = generateDoor(matrix, x_min, x_max, z_min, z_max, h_min+1, h_max, (0,0), (0,0))

	return matrix

def generateBuildingWalls(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall):

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

	# floors division
	cur_floor = h_min
	while cur_floor <= h_max:
		for x in range(x_min, x_max+1):
			for z in range(z_min, z_max+1):
				matrix[cur_floor][x][z] = wall

		cur_floor += floor_size

	return matrix

def generateBuildingWindows(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max):
	z_window_size = random.randint(z_min+2, z_max-2)
	x_window_size = random.randint(x_min+2, x_max-2)

	# windows
	cur_floor = h_min
	while cur_floor < h_max:
	 	width = x_max - x_min
		for x in range(int(width/2) - int(x_window_size/2), int(width/2) + int(math.ceil(x_window_size/2))):
			matrix[cur_floor+int(floor_size/2)][x][z_min] = (20,0)
			matrix[cur_floor+int(floor_size/2)][x][z_max] = (20,0)
			matrix[cur_floor+int(floor_size/2)-1][x][z_min] = (20,0)
			matrix[cur_floor+int(floor_size/2)-1][x][z_max] = (20,0)

		depth = z_max - z_min
		for z in range(int(depth/2) - int(z_window_size/2), int(depth/2) + int(math.ceil(z_window_size/2))):
			matrix[cur_floor+int(floor_size/2)][x_min][z] = (20,0)
			matrix[cur_floor+int(floor_size/2)][x_max][z] = (20,0)
			matrix[cur_floor+int(floor_size/2)-1][x_min][z] = (20,0)
			matrix[cur_floor+int(floor_size/2)-1][x_max][z] = (20,0)

		cur_floor += floor_size
	return matrix


def generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+1][x_min][pos] = (71,9)
		matrix[h_min][x_min][pos] = (71,0)
	elif chance < 0.50:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+1][pos][z_min] = (71,8)
		matrix[h_min][pos][z_min] = (71,1)
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+1][x_max][pos] = (71,9)
		matrix[h_min][x_max][pos] = (71,2)
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+1][pos][z_max] = (71,8)
		matrix[h_min][pos][z_max] = (71,3)

	return matrix