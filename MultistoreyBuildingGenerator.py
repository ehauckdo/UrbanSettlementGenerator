from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math

def buildingGenerator(level,box,options, min_h=20, min_w=8, min_d=8):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

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
	generateBuilding(matrix, 0, height-1, 0, width-1, 0, depth-1, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)


def generateBuilding(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):

	if h_max-h_min < 20 or x_max-x_min < 8 or z_max-z_min < 8:
		return matrix

	wall = (43,random.randint(0,8))
	#wall = (43,15)
	ceiling = wall
	floor = wall
	door = (0,0)

	floor_size = 8
	while (h_max-h_min) % floor_size != 0:
		h_max -= 1

	generateBuildingWalls(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)
	generateBuildingWindows(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max)
	generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, (0,0), (0,0))

def generateHospital(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):

	if h_max-h_min < 20 or x_max-x_min < 8 or z_max-z_min < 8:
		return matrix

	#wall = (43,random.randint(0,8))
	wall = (43,15)
	ceiling = wall
	floor = wall
	door = (0,0)

	floor_size = 8
	while (h_max-h_min) % floor_size != 0:
		h_max -= 1

	generateBuildingWalls(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)
	generateBuildingWindows(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max)
	generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, (0,0), (0,0))

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

def generateBuildingWindows(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max):
	z_window_size = z_max-random.randint(z_min+2, z_max-2)
	x_window_size = x_max-random.randint(x_min+2, x_max-2)

	# windows
	cur_floor = h_min+1
	while cur_floor < h_max:

		window_h = cur_floor + int(math.ceil(floor_size/2))
	 	#width = int(x_max - x_min)
	 	#middle = x_min + int(width/2)
		#for x in range(middle - int(x_window_size/2), middle + int(math.ceil(x_window_size/2)),4):
		for x in range(x_min+1, x_max-1, 3):
			matrix[window_h][x][z_min] = (20,0)
			matrix[window_h][x][z_max] = (20,0)
			matrix[window_h-1][x][z_min] = (20,0)
			matrix[window_h-1][x][z_max] = (20,0)

			matrix[window_h][x+1][z_min] = (20,0)
			matrix[window_h][x+1][z_max] = (20,0)
			matrix[window_h-1][x+1][z_min] = (20,0)
			matrix[window_h-1][x+1][z_max] = (20,0)

		#depth = z_max - z_min
		#middle = z_min + int(depth/2)
		#for z in range(middle - int(z_window_size/2), middle + int(math.ceil(z_window_size/2)),4):
		for z in range(z_min+1, z_max-1, 3):
			matrix[window_h][x_min][z] = (20,0)
		 	matrix[window_h][x_max][z] = (20,0)
		 	matrix[window_h-1][x_min][z] = (20,0)
		 	matrix[window_h-1][x_max][z] = (20,0)

		 	matrix[window_h][x_min][z+1] = (20,0)
		 	matrix[window_h][x_max][z+1] = (20,0)
		 	matrix[window_h-1][x_min][z+1] = (20,0)
		 	matrix[window_h-1][x_max][z+1] = (20,0)

		cur_floor += floor_size

def generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+2][x_min][pos] = (71,9)
		matrix[h_min+1][x_min][pos] = (71,0)
	elif chance < 0.50:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+2][pos][z_min] = (71,8)
		matrix[h_min+1][pos][z_min] = (71,1)
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+2][x_max][pos] = (71,9)
		matrix[h_min+1][x_max][pos] = (71,2)
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+2][pos][z_max] = (71,8)
		matrix[h_min+1][pos][z_max] = (71,3)
