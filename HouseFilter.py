from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
from BinarySpacePartitioning import binarySpacePartitioning

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
	#multiHouseGenerator(level,box,options)
	#houseGenerator(level,box,options)
	buildingGenerator(level,box,options)
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

def multiHouseGenerator(level,box,options, min_h=10):
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
	
	wall = (options["Walls Material Type"].ID, random.randint(options["Walls Material Subtype (min)"],options["Walls Material Subtype (max)"]))
	ceiling = (options["Ceiling Material Type"].ID, random.randint(options["Ceiling Material Subtype (min)"],options["Ceiling Material Subtype (max)"]))
	floor = wall
	door = (0,0)

	ceiling_bottom = h_max -int((h_max-h_min) * 0.5)

	walls_pos = [x_min+1, x_max-1, z_min+1, z_max-1]

	# generate walls from x_min+1, x_max-1, etc to leave space for the ceiling
	matrix = generateWalls(matrix, h_min, ceiling_bottom, h_max, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], wall)
	#matrix = generateWalls(matrix, h_min, h_max, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], wall)

	matrix = generateFloor(matrix, h_min, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], floor)

	matrix = generateDoor(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, door, door)

	matrix = generateWindow(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, wall)

	if random.random() > 0.5:
		matrix = generateCeiling_x(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, wall, 0)
	else:
		matrix = generateCeiling_d(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, wall, 0)

	return matrix

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix[h][x][z] = floor

	return matrix

def generateWalls(matrix, h_min, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix[y][x][z_max] = wall
			matrix[y][x][z_min] = wall

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix[y][x_max][z] = wall
			matrix[y][x_min][z] = wall



	return matrix

def addCeiling(matrix, height, x_min, x_max, z_min, z_max, ceiling):

	# ceiling on every block on uppermost y axis value
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
				matrix[height-1][x][z] = ceiling

	return matrix

def generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	if x_min+recr+1 <= x_max-recr-1:
		for z in range(z_min, z_max+1):
			matrix[h_min+recr][x_min+recr][z] = ceiling
			matrix[h_min+recr][x_max-recr][z] = ceiling
			matrix[h_min+recr][x_min+recr+1][z] = ceiling
			matrix[h_min+recr][x_max-recr-1][z] = ceiling
		for x in range(x_min+recr+2, x_max-recr-1):
			matrix[h_min+recr][x][z_min+1] = wall
			matrix[h_min+recr][x][z_max-1] = wall

	if recr < h_max-h_min:
		matrix  = generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
	 	old_recr = h_min+recr
	 	while x_min+recr+1 < x_max-recr-1:
	 		recr += 1
	 		for z in range (z_min, z_max+1):
	 			matrix[old_recr][x_min+recr+1][z] = ceiling
	 			matrix[old_recr][x_max-recr-1][z] = ceiling

	return matrix

def generateCeiling_d(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	if z_min+recr+1 <= z_max-recr-1:
		for x in range(x_min, x_max+1):
			matrix[h_min+recr][x][z_min+recr] = ceiling
			matrix[h_min+recr][x][z_max-recr] = ceiling
			matrix[h_min+recr][x][z_min+recr+1] = ceiling
			matrix[h_min+recr][x][z_max-recr-1] = ceiling
		for z in range(z_min+recr+2, z_max-recr-1):
			matrix[h_min+recr][x_min+1][z] = wall
			matrix[h_min+recr][x_max-1][z] = wall

	if recr < h_max-h_min:
		matrix  = generateCeiling_d(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
		old_recr = h_min+recr
		while  z_min+recr+1 < z_max-recr-1:
			recr += 1
			for z in range (x_min, x_max+1):
				matrix[h_min+recr][x][z_min+recr+1] = ceiling
				matrix[h_min+recr][x][z_max-recr-1] = ceiling
	return matrix

def generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+1][x_min][pos] = (64,9)
		matrix[h_min][x_min][pos] = (64,0)
	elif chance < 0.50:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+1][pos][z_min] = (64,8)
		matrix[h_min][pos][z_min] = (64,1)
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+1][x_max][pos] = (64,9)
		matrix[h_min][x_max][pos] = (64,2)
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+1][pos][z_max] = (64,8)
		matrix[h_min][pos][z_max] = (64,3)

	return matrix

def generateWindow(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

	# Still need to implement inspection of block before generating!!
	# (properly check if not generating window on top of a door)

	window_height = h_max - int((h_max - h_min)/1.5)
	whmin = h_max - int((h_max - h_min)/1.5)
	whmax = h_max - int((h_max - h_min)/2.5)


	if random.random() < 0.75:
		width = z_max - z_min
		pos_min = random.randint(z_min+int(width*0.1),z_min+int(width*0.4))
		pos_max= random.randint(z_min+int(width*0.6),z_min+int(width*0.9))

		for p in range(pos_min, pos_max):
			for w in range(whmin, whmax):
				matrix[w][x_min][p] = (20,0)

	if random.random() < 0.75:
		width = x_max - x_min
		pos_min = random.randint(x_min+int(width*0.1),x_min+int(width*0.4))
		pos_max= random.randint(x_min+int(width*0.6),x_min+int(width*0.9))

		for p in range(pos_min, pos_max):
			for w in range(whmin, whmax):
				matrix[w][p][z_min] = (20,0)

	if random.random() < 0.75:
		width = z_max - z_min
		pos_min = random.randint(z_min+int(width*0.1),z_min+int(width*0.4))
		pos_max= random.randint(z_min+int(width*0.6),z_min+int(width*0.9))

		for p in range(pos_min, pos_max):
			for w in range(whmin, whmax):
				matrix[w][x_max][p] = (20,0)

	if random.random() < 0.75:
		width = x_max - x_min
		pos_min = random.randint(x_min+int(width*0.1),x_min+int(width*0.4))
		pos_max= random.randint(x_min+int(width*0.6),x_min+int(width*0.9))

		for p in range(pos_min, pos_max):
			for w in range(whmin, whmax):
				matrix[w][p][z_max] = (20,0)

	return matrix

def generateWindowsDeprecated(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):
	window_height = h_max - int((h_max - h_min)/1.5)

	if random.random() < 0.75:
		pos = random.randint(z_min+2,z_max-2)
		matrix[window_height][x_min][pos] = (20,0)
		matrix[window_height-1][x_min][pos] = (20,0)
		matrix[window_height][x_min][pos+1] = (20,0)
		matrix[window_height-1][x_min][pos+1] = (20,0)
	elif random.random() < 0.75:
		pos = random.randint(x_min+2,x_max-2)
		matrix[window_height][pos][z_min] = (20,0)
		matrix[window_height-1][pos][z_min] = (20,0)
		matrix[window_height][pos+1][z_min] = (20,0)
		matrix[window_height-1][pos+1][z_min] = (20,0)
	elif random.random() < 0.75:
		pos = random.randint(z_min+2,z_max-2)
		matrix[window_height][x_max][pos] = (20,0)
		matrix[window_height-1][x_max][pos] = (20,0)
		matrix[window_height][x_max][pos+1] = (20,0)
		matrix[window_height-1][x_max][pos+1] = (20,0)
	elif random.random() < 0.75:
		pos = random.randint(x_min+2,x_max-2)
		matrix[window_height][pos][z_max] = (20,0)
		matrix[window_height-1][pos][z_max] = (20,0)
		matrix[window_height][pos+1][z_max] = (20,0)
		matrix[window_height-1][pos+1][z_max] = (20,0)

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
	generateBuilding(matrix, 0, height-1, 0, width-1, 0, depth-1, options)

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

	z_window_size = random.randint(z_min+2, z_max-2)
	x_window_size = random.randint(x_min+2, x_max-2)

	# floors division
	cur_floor = h_min
	while cur_floor <= h_max:
		for x in range(x_min, x_max+1):
			for z in range(z_min, z_max+1):
				matrix[cur_floor][x][z] = wall

		cur_floor += floor_size

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

	# fix this h_min+1 thing, check how it's working for regular houses
	matrix = generateDoor(matrix, x_min, x_max, z_min, z_max, h_min+1, h_max, (0,0), (0,0))
