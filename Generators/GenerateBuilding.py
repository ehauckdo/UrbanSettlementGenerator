from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
from GenerateObject import *
import math
import RNG
import logging

def generateHospital(matrix, h_min, h_max, x_min, x_max, z_min, z_max):

	utilityFunctions.cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)

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
	generateStairs(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)

def generateBuilding(matrix, h_min, h_max, x_min, x_max, z_min, z_max):

	building = utilityFunctions.dotdict()
	building.type = "building"

	building.area = utilityFunctions.dotdict({"y_min": h_min, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})

	utilityFunctions.cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)

	(h_min, h_max, x_min, x_max, z_min, z_max) = getBuildingAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max)
	building.constructionArea = (h_min, h_max, x_min, x_max, z_min, z_max)

	logging.info("Generating house at area {}".format(building.area))
	logging.info("Construction area {}".format(building.constructionArea))

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
	#if RNG.random() > 0.5:
	building.orientation = "x"
	building.door = generateDoor_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max)
	if building.door[2] == z_min:
		building.entranceLot = (building.door[0], building.door[1], building.area.z_min)
	else:
		building.entranceLot = (building.door[0], building.door[1], building.area.z_max)
	generateBuildingWindows_z(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max)
	#else:
	#	building.orientation = "z"
	#	building.door = generateDoor_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max)
	#	if building.door[1] == x_min:
	#		building.entranceLot = (building.door[0], building.area.x_min, building.door[2])
	#	else:
	#		building.entranceLot = (building.door[0], building.area.x_max, building.door[2])
	#	generateBuildingWindows_z(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max)

	generateStairs(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)
	generateFloorPlan(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall)
	generateInterior(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max-6)

	#for h in range(h_min, 100):
	#	matrix[h][building.entranceLot[1]][building.entranceLot[2]] = (35,2)

	return building

def getBuildingAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max):
	building_size_x = random.randint(15, 18)
	if x_max-x_min > building_size_x:
		x_mid = x_min + (x_max-x_min)/2
		x_min = x_mid - building_size_x/2
		x_max = x_mid + building_size_x/2

	building_size_z = random.randint(15, 18)
	if z_max-z_min > building_size_z:
		z_mid = z_min + (z_max-z_min)/2
		z_min = z_mid - building_size_z/2
		z_max = z_mid + building_size_z/2

	return (h_min, h_max, x_min, x_max, z_min, z_max)

def generateStairs(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall):
	cur_floor = h_min
	floor = 0
	while cur_floor < h_max:
		step = cur_floor+floor_size-1
		if floor % 2 == 0:
			x = x_max-2
			z = z_max-2
			for x1 in range(x, x-3, -1):
				matrix.setValue(step+1, x1, z, (0, 0))
				matrix.setValue(step+1, x1, z-1, (0, 0))

			while step > cur_floor:
				matrix.setValue(step, x, z, (109, 0))
				matrix.setValue(step, x, z-1, (109, 0))
				for h in range(cur_floor+1, step):
					matrix.setValue(h, x, z, (98, 0))
					matrix.setValue(h, x, z-1, (98, 0))
				
				step -= 1
				x -= 1
		if floor % 2 == 1:
			x = x_min+2
			z = z_max-2
			for x1 in range(x, x+3):
				matrix.setValue(step+1, x1, z, (0, 0))
				matrix.setValue(step+1, x1, z-1, (0, 0))
			while step > cur_floor:
				matrix.setValue(step, x, z, (109, 1))
				matrix.setValue(step, x, z-1, (109, 1))
				for h in range(cur_floor+1, step):
					matrix.setValue(h, x, z, (98, 0))
					matrix.setValue(h, x, z-1, (98, 0))
				step -= 1
				x += 1	

		floor += 1
		cur_floor += floor_size

def generateFloorPlan(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall):

	cur_floor = h_min
	cur_floor_ceiling = cur_floor+floor_size
	while cur_floor < h_max:
		# generating separating wall between hall and apartments
		for h in range(cur_floor, cur_floor+floor_size):
			for x in range(x_min, x_max):
				matrix.setValue(h, x, z_max-6, wall)

		# generating door to the apartment
		door_x = x_max - ((x_max-x_min)/2)
		matrix.setValue(cur_floor+2, door_x, z_max-6, (64,8))
		matrix.setValue(cur_floor+1, door_x, z_max-6, (64,8))

		cur_floor += floor_size

def generateInterior(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max):
	
	cur_floor = h_min
	cur_floor_ceiling = cur_floor+floor_size
	floor = 0
	x_mid = x_max - int((x_max - x_min)/2)
	z_mid = z_max - int((z_max - z_min)/2)
	
	while cur_floor < h_max:

		# bed
		#matrix.setValue(h_min+1, x_max-1, z_min+1, (26,11)
		#matrix.setValue(h_min+1, x_max-2, z_min+1, (26,3)

		# bed (wool)
		generateBed(matrix, cur_floor, x_max, z_min)

		# table
		generateCentralTable(matrix, cur_floor, x_mid, z_mid)

		# bookshelf
		generateBookshelf(matrix, cur_floor, x_max, z_max)

		# couch
		generateCouch(matrix, cur_floor, x_min, z_max)

		# chandelier
		x_mid = x_min + (x_max-x_min)/2
		z_mid = z_min + (z_max-z_min)/2
		generateChandelier(matrix, cur_floor_ceiling, x_mid, z_mid)

		cur_floor += floor_size

def generateBuildingWalls(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, h_max):
			matrix.setValue(y,x,z_max, wall)
			matrix.setValue(y,x,z_min, wall)

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, h_max):
			matrix.setValue(y,x_max,z, wall)
			matrix.setValue(y,x_min,z, wall)

	# floors division
	cur_floor = h_min
	while cur_floor <= h_max:
		for x in range(x_min, x_max+1):
			for z in range(z_min, z_max+1):
				matrix.setValue(cur_floor,x,z, wall)

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

			matrix.setValue(window_h, x, z_min, (20,0))
			matrix.setValue(window_h, x, z_max, (20,0))
			matrix.setValue(window_h-1, x, z_min, (20,0))
			matrix.setValue(window_h-1, x, z_max, (20,0))

			matrix.setValue(window_h, x+1, z_min, (20,0))
			matrix.setValue(window_h, x+1, z_max, (20,0))
			matrix.setValue(window_h-1, x+1, z_min, (20,0))
			matrix.setValue(window_h-1, x+1, z_max, (20,0))

		#depth = z_max - z_min
		#middle = z_min + int(depth/2)
		#for z in range(middle - int(z_window_size/2), middle + int(math.ceil(z_window_size/2)),4):
		for z in range(z_min+1, z_max-1, 3):

		 	matrix.setValue(window_h, x_min, z, (20,0))
		 	matrix.setValue(window_h, x_max, z, (20,0))
		 	matrix.setValue(window_h-1, x_min, z, (20,0))
		 	matrix.setValue(window_h-1, x_max, z, (20,0))

		 	matrix.setValue(window_h, x_min, z+1, (20,0))
		 	matrix.setValue(window_h, x_max, z+1, (20,0))
		 	matrix.setValue(window_h-1, x_min, z+1, (20,0))
		 	matrix.setValue(window_h-1, x_max, z+1, (20,0))

		cur_floor += floor_size

def generateBuildingWindows_x(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max):
	z_window_size = z_max-random.randint(z_min+2, z_max-2)

	# windows
	cur_floor = h_min+1
	while cur_floor < h_max:

		window_h = cur_floor + int(math.ceil(floor_size/2))
	 
		#depth = z_max - z_min
		#middle = z_min + int(depth/2)
		#for z in range(middle - int(z_window_size/2), middle + int(math.ceil(z_window_size/2)),4):
		for z in range(z_min+1, z_max-1, 3):

		 	matrix.setValue(window_h, x_min, z, (20,0))
		 	matrix.setValue(window_h-1, x_min, z, (20,0))
		 	matrix.setValue(window_h, x_min, z+1, (20,0))
		 	matrix.setValue(window_h-1, x_min, z+1, (20,0))

		cur_floor += floor_size

def generateBuildingWindows_z(matrix, h_min, h_max, floor_size, x_min, x_max, z_min, z_max):
	x_window_size = x_max-random.randint(x_min+2, x_max-2)

	# windows
	cur_floor = h_min+1
	while cur_floor < h_max:

		
		window_h = cur_floor + int(math.ceil(floor_size/2))
		for x in range(x_min+2, x_max-1, 3):
			# apartment windows
			matrix.setValue(window_h, x, z_min, (20,0))
			matrix.setValue(window_h-1, x, z_min, (20,0))
			matrix.setValue(window_h, x+1, z_min, (20,0))
			matrix.setValue(window_h-1, x+1, z_min, (20,0))

			# corridor windows
			matrix.setValue(window_h, x, z_max, (20,0))
			matrix.setValue(window_h-1, x, z_max, (20,0))
			matrix.setValue(window_h, x+1, z_max, (20,0))
			matrix.setValue(window_h-1, x+1, z_max, (20,0))


		cur_floor += floor_size

def generateDoor(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	chance = random.random()
	if chance < 0.25:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+2][x_min][pos] = (64,9)
		matrix[h_min+1][x_min][pos] = (64,0)
		return (h_min+1, x_min, pos)
	elif chance < 0.50:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+2][pos][z_min] = (64,8)
		matrix[h_min+1][pos][z_min] = (64,1)
		return (h_min+1, pos, z_min)
	elif chance < 0.75:
		pos = random.randint(z_min+1,z_max-1)
		matrix[h_min+2][x_max][pos] = (64,9)
		matrix[h_min+1][x_max][pos] = (64,2)
		return (h_min+1, x_max, pos)
	else:
		pos = random.randint(x_min+1,x_max-1)
		matrix[h_min+2][pos][z_max] = (64,8)
		matrix[h_min+1][pos][z_max] = (64,3)
		return (h_min+1, pos, z_max)

def generateDoor_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max):

	lader_space = x_max-8
	pos = RNG.randint(x_min+1, lader_space)
	#pos = x_min+1
	#chance = RNG.random()
	#if chance < 0.50:
	#matrix[h_min+2][pos][z_min] = (64,8)
	#matrix[h_min+1][pos][z_min] = (64,1)
	#return (h_min, pos, z_min)
	#else:
	matrix.setValue(h_min+2, pos, z_max, (64,8))
	matrix.setValue(h_min+1, pos, z_max, (64,8))
	return (h_min, pos, z_max)

def generateDoor_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max):

	lader_space = z_max-8
	pos = RNG.randint(z_min+1, lader_space)
	#pos = z_min+1
	#chance = RNG.random()
	#if chance < 0.50:
	#matrix[h_min+2][x_min][pos] = (64,9)
	#matrix[h_min+1][x_min][pos] = (64,0)
	#return (h_min, x_min, pos)
	#else:
	matrix.setValue(h_min+2, x_max, pos, (64,9))
	matrix.setValue(h_min+1, x_max, pos, (64,2))
	return (h_min, x_max, pos)
