from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
from GenerateCarpet import generateCarpet
import random
import math
import RNG
import logging

def generateHouse(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options, ceiling = (5, RNG.randint(1,5))):

	house = utilityFunctions.dotdict()
	house.type = "house"
	#house.area = (h_min, h_max, x_min, x_max, z_min, z_max)
	house.area = utilityFunctions.dotdict({"y_min": h_min, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})

	cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)
	generateFence(matrix, h_min, x_min, x_max, z_min, z_max)

	(h_min, h_max, x_min, x_max, z_min, z_max) = getHouseAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max)
	
	logging.info("Generating house at area {}".format(house.area))
	logging.info("Construction area {}".format((h_min, h_max, x_min, x_max, z_min, z_max)))
	
	#wall = (options["Walls Material Type"].ID, RNG.randint(options["Walls Material Subtype (min)"],options["Walls Material Subtype (max)"]))
	#ceiling = (options["Ceiling Material Type"].ID, RNG.randint(options["Ceiling Material Subtype (min)"],options["Ceiling Material Subtype (max)"]))
	wall = (43, RNG.randint(11,15))
	#ceiling = (5, RNG.randint(1,5))
	floor = wall
	door = (0,0)

	ceiling_bottom = h_max -int((h_max-h_min) * 0.5)
	#print("ceiling_bottom", ceiling_bottom)
	house.constructionArea = (h_min, ceiling_bottom, x_min, x_max, z_min, z_max)

	#walls_pos = [x_min+1, x_max-1, z_min+1, z_max-1]
	walls_pos = [x_min, x_max, z_min, z_max]

	# generate walls from x_min+1, x_max-1, etc to leave space for the roof
	generateWalls(matrix, h_min, ceiling_bottom, h_max, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], wall)
	generateFloor(matrix, h_min, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], floor)

	if RNG.random() > 0.5:
		house.orientation = "x"
		house.door = generateDoor_x(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, door, door)
		if house.door[2] == walls_pos[2]:
			house.entranceLot = (house.door[0], house.door[1], house.area.z_min)
			try:
				for x in range(house.door[1]-1, house.door[1]+2):
					matrix[house.door[0]][x][house.area.z_min+1] = (0,0)
			except:
				# there is a possibility of house.door[1]-1 or
				# house.door[1]+2 being out of range
				pass
		else:
			house.entranceLot = (house.door[0], house.door[1], house.area.z_max)
			try:
				for x in range(house.door[1]-1, house.door[1]+2):
					matrix[house.door[0]][x][house.area.z_max-1] = (0,0)
			except:
				# there is a possibility of house.door[1]-1 or
				# house.door[1]+2 being out of range
				pass
		generateWindow_x(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, wall)
		generateCeiling_x(matrix, ceiling_bottom, h_max, x_min-1, x_max+1, z_min-1, z_max+1, ceiling, wall, 0)
	else:
		house.orientation = "z"
		house.door = generateDoor_z(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, door, door)
		if house.door[1] == walls_pos[0]:
			house.entranceLot = (house.door[0], house.area.x_min, house.door[2])
			try:
				for z in range(house.door[2]-1, house.door[2]+2):
					matrix[house.door[0]][house.area.x_min+1][z] = (0,0)
			except:
				# there is a possibility of house.door[1]-1 or
				# house.door[1]+2 being out of range
				pass
		else:
			house.entranceLot = (house.door[0], house.area.x_max, house.door[2])
			try:
				for z in range(house.door[2]-1, house.door[2]+2):
					matrix[house.door[0]][house.area.x_max-1][z] = (0,0)
			except:
				# there is a possibility of house.door[1]-1 or
				# house.door[1]+2 being out of range
				pass
		generateWindow_z(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, wall)
		generateCeiling_z(matrix, ceiling_bottom, h_max, x_min-1, x_max+1, z_min-1, z_max+1, ceiling, wall, 0)


	generateInterior(matrix, h_min, ceiling_bottom, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], ceiling)

	#for h in range(h_min, 100):
	#	matrix[h][house.entranceLot[1]][house.entranceLot[2]] = (35,2)

	return house

def getHouseAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max):
	house_size_x = RNG.randint(10, 14)
	if x_max-x_min > house_size_x:
		x_mid = x_min + (x_max-x_min)/2
		x_min = x_mid - house_size_x/2
		x_max = x_mid + house_size_x/2

	house_size_z = RNG.randint(10, 14)
	if z_max-z_min > house_size_z:
		z_mid = z_min + (z_max-z_min)/2
		z_min = z_mid - house_size_z/2
		z_max = z_mid + house_size_z/2

	house_size_h = (house_size_x+house_size_z)/2
	if h_max-h_min > 15 or h_max-h_min > house_size_h: 
		h_max = h_min+ ((house_size_x+house_size_z)/2)

	return (h_min, h_max, x_min, x_max, z_min, z_max)
	
def cleanProperty(matrix, h_min, h_max, x_min, x_max, z_min, z_max):
	for h in range(h_min, h_max):
		for x in range(x_min, x_max+1):
			for z in range(z_min, z_max+1):
				matrix[h][x][z] = (0,0)

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix[h][x][z] = floor

def generateFence(matrix, h, x_min, x_max, z_min, z_max):
	#for x in range(x_min, x_max+1):
	#	matrix[h][x][z_max] = (4,0)
	#	matrix[h][x][z_min] = (4,0)
	#for z in range(z_min+1, z_max):
	#	matrix[h][x_max][z] = (4,0)
	#	matrix[h][x_min][z] = (4,0)

	for x in range(x_min+1, x_max):
		matrix[h+1][x][z_max-1] = (85,0)
		matrix[h+1][x][z_min+1] = (85,0)
	for z in range(z_min+1, z_max):
		matrix[h+1][x_max-1][z] = (85,0)
		matrix[h+1][x_min+1][z] = (85,0)

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

def generateInterior(matrix, h_min, h_max, x_min, x_max, z_min, z_max, wood):
	
	# bed (actual bed, bugged)
	#matrix[h_min+1][x_max-1][z_min+1] = (26,11)
	#matrix[h_min+1][x_max-2][z_min+1] = (26,3)

	generateCarpet(matrix, h_min+1, x_min+1, x_max, z_min+1, z_max)

	# bed (wool)
	matrix[h_min+1][x_max-1][z_min+1] = (35,14)
	matrix[h_min+1][x_max-2][z_min+1] = (35,14)

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

	# chandelier
	x_mid = x_min + (x_max-x_min)/2
	z_mid = z_min + (z_max-z_min)/2
	for z in range(z_min+1, z_max):
		matrix[h_max][x_mid][z] = wood
	matrix[h_max-1][x_mid][z_mid] = (85,0)
	matrix[h_max-2][x_mid][z_mid] = (169,0)

# def generateCarpet(matrix, h, x_min, x_max, z_min, z_max):
# 	carpetID = 171
# 	carpetSubtype = RNG.randint(0, 14)

# 	for x in range(x_min, x_max):
# 		for z in range(z_min, z_max):
# 			matrix[h][x][z] = (carpetID, carpetSubtype)

def generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	#print("Recursive step ", recr)
	#print("h_min", h_min,"h_max", h_max,"x_min", x_min, "h_max", x_max, "z_min", z_min,"z_max", z_max)
	if x_min+recr+1 <= x_max-recr-1:
		for z in range(z_min, z_max+1):					  # intended pitched roof effect
			#print("testing z ", z)
			matrix[h_min+recr][x_min+recr][z] = ceiling   #       _  
			matrix[h_min+recr][x_max-recr][z] = ceiling   #     _| |_
			matrix[h_min+recr][x_min+recr+1][z] = ceiling #   _|     |_
			matrix[h_min+recr][x_max-recr-1][z] = ceiling # _|         |_
		for x in range(x_min+recr+2, x_max-recr-1):		
			#print("testing x ", x)
			matrix[h_min+recr][x][z_min+1] = wall 		  # fill front and back part of the roof
			matrix[h_min+recr][x][z_max-1] = wall

	if recr < h_max-h_min:
		generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
	 	old_recr = h_min+recr
	 	while x_min+recr+1 < x_max-recr-1:
	 		recr += 1
	 		for z in range (z_min, z_max+1):
	 			matrix[old_recr][x_min+recr+1][z] = ceiling
	 			matrix[old_recr][x_max-recr-1][z] = ceiling

def generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	#print("Recursive step ", recr)
	#print("h_min", h_min,"h_max", h_max,"x_min", x_min, "h_max", x_max, "z_min", z_min,"z_max", z_max)
	if z_min+recr+1 <= z_max-recr-1:
		for x in range(x_min, x_max+1):
			#print("testing x ", x)
			matrix[h_min+recr][x][z_min+recr] = ceiling
			matrix[h_min+recr][x][z_max-recr] = ceiling
			matrix[h_min+recr][x][z_min+recr+1] = ceiling
			matrix[h_min+recr][x][z_max-recr-1] = ceiling
		for z in range(z_min+recr+2, z_max-recr-1):
			#print("testing z ", z)
			matrix[h_min+recr][x_min+1][z] = wall
			matrix[h_min+recr][x_max-1][z] = wall

	if recr < h_max-h_min:
		generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
		old_recr = h_min+recr
		while  z_min+recr+1 < z_max-recr-1:
			recr += 1
			for x in range (x_min, x_max+1):
				matrix[old_recr][x][z_min+recr+1] = ceiling
				matrix[old_recr][x][z_max-recr-1] = ceiling

def generateDoor_x(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	pos = RNG.randint(x_min+1,x_max-1)
	chance = RNG.random()
	if chance < 0.50:
		matrix[h_min+1][pos][z_min] = (64,8)
		matrix[h_min][pos][z_min] = (64,1)
		return (h_min, pos, z_min)
	else:
		matrix[h_min+1][pos][z_max] = (64,8)
		matrix[h_min][pos][z_max] = (64,3)
		return (h_min, pos, z_max)

def generateDoor_z(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	pos = RNG.randint(z_min+1,z_max-1)
	chance = RNG.random()
	if chance < 0.50:
		matrix[h_min+1][x_min][pos] = (64,9)
		matrix[h_min][x_min][pos] = (64,0)
		return (h_min, x_min, pos)
	else:
		matrix[h_min+1][x_max][pos] = (64,9)
		matrix[h_min][x_max][pos] = (64,2)
		return (h_min, x_max, pos)

def generateWindow_x(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

	window_height = h_max - int((h_max - h_min)/1.5)
	whmin = h_max - int((h_max - h_min)/1.5)
	whmax = h_max - int((h_max - h_min)/2.5)

	width = z_max - z_min
	pos_min = RNG.randint(z_min+int(width*0.1),z_min+int(width*0.4))
	pos_max = RNG.randint(z_min+int(width*0.6),z_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][x_min][p] = (20,0)

	width = z_max - z_min
	pos_min = RNG.randint(z_min+int(width*0.1),z_min+int(width*0.4))
	pos_max = RNG.randint(z_min+int(width*0.6),z_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][x_max][p] = (20,0)

def generateWindow_z(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

	window_height = h_max - int((h_max - h_min)/1.5)
	whmin = h_max - int((h_max - h_min)/1.5)
	whmax = h_max - int((h_max - h_min)/2.5)

	width = x_max - x_min
	pos_min = RNG.randint(x_min+int(width*0.1),x_min+int(width*0.4))
	pos_max= RNG.randint(x_min+int(width*0.6),x_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][p][z_min] = (20,0)

	width = x_max - x_min
	pos_min = RNG.randint(x_min+int(width*0.1),x_min+int(width*0.4))
	pos_max= RNG.randint(x_min+int(width*0.6),x_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][p][z_max] = (20,0)
