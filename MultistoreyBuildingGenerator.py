from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math

def generateBuilding(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):

	cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)

	x_min += 3
	x_max -= 3
	z_min += 3
	z_max -= 3

	if h_max-h_min < 20 or x_max-x_min < 8 or z_max-z_min < 8:
		return matrix

	#wall = (43,random.randint(0,8))
	wall = (159,random.randint(0,15))
	ceiling = wall
	floor = wall
	door = (0,0)

	floor_size = 8
	if h_max-h_min > 82:
		h_max = h_min+random.randint(36, 82)
		
	while (h_max-h_min) % floor_size != 0:
		h_max -= 1

	generateBuildingWalls(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)
	generateBuildingWindows(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max)
	generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, (0,0), (0,0))
	generateFloors_new(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)

def generateFloors(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max):
	#print("Generating interior!")
	cur_floor = h_min
	floor = 0
	while cur_floor <= h_max:
		step = cur_floor+floor_size-1
		if floor % 4 == 0:
			#print("At 3")
			x = x_max-1
			z = z_max-1
			# hole to go up to upper floor
			for x1 in range(x, x-3, -1):
				matrix[step+1][x1][z] = (0, 0)
				matrix[step+1][x1][z-1] = (0, 0)

			while step > cur_floor:
				#print("Generating stairs at step ", step)
				# stairs
				matrix[step][x][z] = (109, 0)
				matrix[step][x][z-1] = (109, 0)
				#foundation
				for h in range(cur_floor+1, step):
					matrix[h][x][z] = (98, 0)
					matrix[h][x][z-1] = (98, 0)
				
				step -= 1
				x -= 1
		if floor % 4 == 1:
			#print("At 2")
			x = x_max-1
			z = z_min+1
			for z1 in range(z, z+3):
				matrix[step+1][x][z1] = (0, 0)
				matrix[step+1][x-1][z1] = (0, 0)
			while step > cur_floor:
				#print("Generating stairs at step ", step)
				matrix[step][x][z] = (109, 3)
				matrix[step][x-1][z] = (109, 3)
				for h in range(cur_floor+1, step):
					matrix[h][x][z] = (98, 0)
					matrix[h][x-1][z] = (98, 0)
				step -= 1
				z += 1
		if floor % 4 == 2:
			#print("At 1")
			x = x_min+1
			z = z_min+1
			for x1 in range(x, x+3):
				matrix[step+1][x1][z] = (0, 0)
				matrix[step+1][x1][z+1] = (0, 0)
			while step > cur_floor:
				#print("Generating stairs at step ", step)
				matrix[step][x][z] = (109, 1)
				matrix[step][x][z+1] = (109, 1)
				for h in range(cur_floor+1, step):
					matrix[h][x][z] = (98, 0)
					matrix[h][x][z+1] = (98, 0)
				step -= 1
				x += 1
		if floor % 4 == 3:
			#print("At 1")
			x = x_min+1
			z = z_max-1
			for z1 in range(z, z-3, -1):
				matrix[step+1][x][z1] = (0, 0)
				matrix[step+1][x+1][z1] = (0, 0)
			while step > cur_floor:
				#print("Generating stairs at step ", step)
				matrix[step][x][z] = (109, 2)
				matrix[step][x+1][z] = (109, 2)
				for h in range(cur_floor+1, step):
					matrix[h][x][z] = (98, 0)
					matrix[h][x+1][z] = (98, 0)
				step -= 1
				z -= 1
		floor += 1
		cur_floor += floor_size

def generateFloors_new(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall):
	#print("Generating interior!")
	cur_floor = h_min
	floor = 0
	while cur_floor < h_max:
		step = cur_floor+floor_size-1
		if floor % 2 == 0:
			x = x_max-1
			z = z_max-1
			for x1 in range(x, x-3, -1):
				matrix[step+1][x1][z] = (0, 0)
				matrix[step+1][x1][z-1] = (0, 0)

			while step > cur_floor:
				matrix[step][x][z] = (109, 0)
				matrix[step][x][z-1] = (109, 0)
				for h in range(cur_floor+1, step):
					matrix[h][x][z] = (98, 0)
					matrix[h][x][z-1] = (98, 0)
				
				step -= 1
				x -= 1
		if floor % 2 == 1:
			x = x_min+1
			z = z_max-1
			for x1 in range(x, x+3):
				matrix[step+1][x1][z] = (0, 0)
				matrix[step+1][x1][z-1] = (0, 0)
			while step > cur_floor:
				matrix[step][x][z] = (109, 1)
				matrix[step][x][z-1] = (109, 1)
				for h in range(cur_floor+1, step):
					matrix[h][x][z] = (98, 0)
					matrix[h][x][z-1] = (98, 0)
				step -= 1
				x += 1

		# generating separating wall between hall and apartments
		for h in range(cur_floor, cur_floor+floor_size):
			for x in range(x_min, x_max):
				matrix[h][x][z_max-6] = wall

		door_x = x_max - ((x_max-x_min)/2)
		matrix[cur_floor+2][door_x][z_max-6] = (64,8)
		matrix[cur_floor+1][door_x][z_max-6] = (64,3)

		generateInterior(matrix, cur_floor, cur_floor+floor_size, x_min, x_max, z_min, z_max-6)		

		floor += 1
		cur_floor += floor_size

def generateInterior(matrix, h_min, ceiling_bottom, x_min, x_max, z_min, z_max):
	
	# bed
	matrix[h_min+1][x_max-1][z_min+1] = (26,11)
	matrix[h_min+1][x_max-2][z_min+1] = (26,3)

	x_mid = x_max - int((x_max - x_min)/2)
	z_mid = z_max - int((z_max - z_min)/2)

	# table
	matrix[h_min+1][x_mid][z_mid] = (85,0)
	matrix[h_min+2][x_mid][z_mid] = (72,0)
	matrix[h_min+1][x_mid-1][z_mid] = (53, 1)
	matrix[h_min+1][x_mid+1][z_mid] = (53, 0)

	# bookshelf
	matrix[h_min+1][x_max-1][z_max-1] = (47,0)
	matrix[h_min+1][x_max-2][z_max-1] = (47,0)
	matrix[h_min+2][x_max-1][z_max-1] = (47,0)
	matrix[h_min+2][x_max-2][z_max-1] = (47,0)

	# couch
	matrix[h_min+1][x_min+4][z_max-1] = (68, 5)
	matrix[h_min+1][x_min+3][z_max-1] = (53, 2)
	matrix[h_min+1][x_min+2][z_max-1] = (53, 2)
	matrix[h_min+1][x_min+1][z_max-1] = (68, 4)

def generateHospital(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):

	cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)

	hospitalPartition = utilityFunctions.getSubsection(x_min, x_max, z_min, z_max, 0.8)
	x_min = hospitalPartition[0]
	x_max = hospitalPartition[1]
	z_min = hospitalPartition[2]
	z_max = hospitalPartition[3]

	if h_max-h_min < 20 or x_max-x_min < 8 or z_max-z_min < 8:
		return matrix

	#wall = (43,random.randint(0,8))
	wall = (43,15)
	ceiling = wall
	floor = wall
	door = (0,0)

	floor_size = 8
	if h_max-h_min > 82:
		h_max = h_min+82

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
		matrix[h_min+2][x_min][pos] = (64,9)
		matrix[h_min+1][x_min][pos] = (64,0)
	elif chance < 0.50:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+2][pos][z_min] = (64,8)
		matrix[h_min+1][pos][z_min] = (64,1)
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+2][x_max][pos] = (64,9)
		matrix[h_min+1][x_max][pos] = (64,2)
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+2][pos][z_max] = (64,8)
		matrix[h_min+1][pos][z_max] = (64,3)

def cleanProperty(matrix, h_min, h_max, x_min, x_max, z_min, z_max):
	for h in range(h_min, h_max):
		for x in range(x_min, x_max+1):
			for z in range(z_min, z_max+1):
				matrix[h][x][z] = (0,0)
