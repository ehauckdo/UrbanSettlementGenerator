from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
from GenerateCarpet import generateCarpet
from GenerateObject import *
import random
import math
import RNG
import logging

def generateHouse(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling = None):

	house = utilityFunctions.dotdict()
	house.type = "house"
	house.lotArea = utilityFunctions.dotdict({"y_min": h_min, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})

	utilityFunctions.cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)
	generateFence(matrix, h_min, x_min, x_max, z_min, z_max)

	(h_min, h_max, x_min, x_max, z_min, z_max) = getHouseAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max)
	ceiling_bottom = h_max -int((h_max-h_min) * 0.5)
	house.buildArea = utilityFunctions.dotdict({"y_min": h_min, "y_max": ceiling_bottom, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
	
	logging.info("Generating house at area {}".format(house.lotArea))
	logging.info("Construction area {}".format(house.buildArea))
	
	wall = (43, RNG.randint(11,15))
	ceiling = (5, RNG.randint(1,5)) if ceiling == None else ceiling
	floor = wall
	door = (0,0)

	# generate walls from x_min+1, x_max-1, etc to leave space for the roof
	generateWalls(matrix, house.buildArea.y_min, house.buildArea.y_max, house.buildArea.x_min, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max, wall)
	generateFloor(matrix, house.buildArea.y_min, house.buildArea.x_min, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max, floor)

	house.orientation = getOrientation(matrix, house.lotArea)
	window_y = house.buildArea.y_min + (house.buildArea.y_max-house.buildArea.y_min)/2
	door_y = house.buildArea.y_min + 1
	
	if house.orientation == "N":
		door_x = RNG.randint(house.buildArea.x_min+1, house.buildArea.x_max-1)
		door_z = house.buildArea.z_min
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,1))
		house.entranceLot = (h_min+1, door_x, house.lotArea.z_min)
		
	elif house.orientation == "S":
		door_x = RNG.randint(house.buildArea.x_min+1, house.buildArea.x_max-1)
		door_z = house.buildArea.z_max
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,3))
		house.entranceLot = (h_min+1, door_x, house.lotArea.z_max)

	elif house.orientation == "W":
		door_x = house.buildArea.x_min
		door_z = RNG.randint(house.buildArea.z_min+1, house.buildArea.z_max-1)
		generateDoor(matrix, door_y, door_x, door_z, (64,8), (64,0))
		house.entranceLot = (h_min+1, house.lotArea.x_min, door_x) 

	elif house.orientation == "E":
		door_x = house.buildArea.x_max
		door_z = RNG.randint(house.buildArea.z_min+1, house.buildArea.z_max-1)
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,2))
		house.entranceLot = (h_min+1, house.lotArea.x_max, door_x) 

	if house.orientation == "N" or house.orientation == "S":
		generateWindow_alongX(matrix, window_y, house.buildArea.x_min, house.buildArea.z_min, house.buildArea.z_max)
		generateWindow_alongX(matrix, window_y, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max)
		generateCeiling_x(matrix, ceiling_bottom, h_max, x_min-1, x_max+1, z_min-1, z_max+1, ceiling, wall, 0)
	elif house.orientation == "E" or house.orientation == "W":
		generateWindow_alongZ(matrix, window_y, house.buildArea.z_min, house.buildArea.x_min, house.buildArea.x_max)
		generateWindow_alongZ(matrix, window_y, house.buildArea.z_max, house.buildArea.x_min, house.buildArea.x_max)
		generateCeiling_z(matrix, ceiling_bottom, h_max, x_min-1, x_max+1, z_min-1, z_max+1, ceiling, wall, 0)

	generateInterior(matrix, h_min, ceiling_bottom, house.buildArea.x_min, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max, ceiling)

	#for h in range(h_min, 100):
	#	matrix.setValue(h, house.entranceLot[1], house.entranceLot[2], (35,2))

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

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix.setValue(h,x,z,floor)

def generateFence(matrix, h, x_min, x_max, z_min, z_max):

	for x in range(x_min+1, x_max):
		matrix.setValue(h+1, x, z_max-1, (85,0))
		matrix.setValue(h+1, x, z_min+1, (85,0))
	for z in range(z_min+1, z_max):
		matrix.setValue(h+1, x_max-1, z, (85,0))
		matrix.setValue(h+1, x_min+1, z, (85,0))

def generateWalls(matrix, h_min, ceiling_bottom, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix.setValue(y,x,z_max, wall)
			matrix.setValue(y,x,z_min, wall)

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix.setValue(y,x_max,z, wall)
			matrix.setValue(y,x_min,z, wall)

def generateInterior(matrix, h_min, h_max, x_min, x_max, z_min, z_max, wood):
	
	# bed (actual bed, bugged)
	#matrix[h_min+1][x_max-1][z_min+1] = (26,11)
	#matrix[h_min+1][x_max-2][z_min+1] = (26,3)

	generateCarpet(matrix.matrix, h_min+1, x_min+1, x_max, z_min+1, z_max)

	# bed (wool)
	generateBed(matrix, h_min, x_max, z_min)

	x_mid = x_max - int((x_max - x_min)/2)
	z_mid = z_max - int((z_max - z_min)/2)

	# table
	generateCentralTable(matrix, h_min, x_mid, z_mid)

	# bookshelf
	generateBookshelf(matrix, h_min, x_max, z_max)

	# couch
	generateCouch(matrix, h_min, x_min, z_max)

	# chandelier
	x_mid = x_min + (x_max-x_min)/2
	z_mid = z_min + (z_max-z_min)/2
	for z in range(z_min+1, z_max):
		matrix.setValue(h_max, x_mid, z, wood)
	generateChandelier(matrix, h_max, x_mid, z_mid)


def generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	#print("Recursive step ", recr)
	#print("h_min", h_min,"h_max", h_max,"x_min", x_min, "h_max", x_max, "z_min", z_min,"z_max", z_max)
	if x_min+recr+1 <= x_max-recr-1:
		for z in range(z_min, z_max+1):					  # intended pitched roof effect
			#print("testing z ", z)
			matrix.setValue(h_min+recr, x_min+recr, z, ceiling)   #       _  
			matrix.setValue(h_min+recr, x_max-recr, z, ceiling)   #     _| |_
			matrix.setValue(h_min+recr, x_min+recr+1, z, ceiling) #   _|     |_
			matrix.setValue(h_min+recr, x_max-recr-1, z, ceiling) # _|         |_
		for x in range(x_min+recr+2, x_max-recr-1):		
			#print("testing x ", x)
			matrix.setValue(h_min+recr, x, z_min+1, wall) # fill front and back part of the roof
			matrix.setValue(h_min+recr, x, z_max-1, wall)

	if recr < h_max-h_min:
		generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
	 	old_recr = h_min+recr
	 	while x_min+recr+1 < x_max-recr-1:
	 		recr += 1
	 		for z in range (z_min, z_max+1):
	 			matrix.setValue(old_recr, x_min+recr+1, z, ceiling)
				matrix.setValue(old_recr, x_max-recr-1, z, ceiling)

def generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	#print("Recursive step ", recr)
	#print("h_min", h_min,"h_max", h_max,"x_min", x_min, "h_max", x_max, "z_min", z_min,"z_max", z_max)
	if z_min+recr+1 <= z_max-recr-1:
		for x in range(x_min, x_max+1):
			#print("testing x ", x)
			matrix.setValue(h_min+recr, x, z_min+recr, ceiling)
			matrix.setValue(h_min+recr, x, z_max-recr, ceiling)
			matrix.setValue(h_min+recr, x, z_min+recr+1, ceiling)
			matrix.setValue(h_min+recr, x, z_max-recr-1, ceiling)
		for z in range(z_min+recr+2, z_max-recr-1):
			#print("testing z ", z)
			matrix.setValue(h_min+recr, x_min+1, z, wall)
			matrix.setValue(h_min+recr, x_max-1, z, wall)

	if recr < h_max-h_min:
		generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
		old_recr = h_min+recr
		while  z_min+recr+1 < z_max-recr-1:
			recr += 1
			for x in range (x_min, x_max+1):
				matrix.setValue(old_recr, x, z_min+recr+1, ceiling)
				matrix.setValue(old_recr, x, z_max-recr-1, ceiling)

def generateDoor(matrix, y, x, z, door_up, door_down):
	matrix.setValue(y+1, x, z, door_up)
	matrix.setValue(y, x, z, door_down)


# The next two functions do the same thing, but they are
# separated for more clear understanding
def generateWindow_alongX(matrix, h, x, z_min, z_max):
	for z in range(z_min+2, z_max-2, 3):
		 	matrix.setValue(h, x, z, (20,0))
		 	matrix.setValue(h-1, x, z, (20,0))
		 	matrix.setValue(h, x, z+1, (20,0))
		 	matrix.setValue(h-1, x, z+1, (20,0))

def generateWindow_alongZ(matrix, h, z, x_min, x_max):
	for x in range(x_min+2, x_max-2, 3):

			matrix.setValue(h, x, z, (20,0))
			matrix.setValue(h-1, x, z, (20,0))
			matrix.setValue(h, x+1, z, (20,0))
			matrix.setValue(h-1, x+1, z, (20,0))

def getOrientation(matrix, area):
	x_mid = matrix.width/2
	z_mid = matrix.depth/2

	bx_mid = area.x_min + (area.x_max-area.x_min)/2
	bz_mid = area.z_min + (area.z_max-area.z_min)/2

	if bx_mid <= x_mid:
		if bz_mid <= z_mid:
			#SOUTH, EAST
			return RNG.choice(["S", "E"])
		elif bz_mid > z_mid:
			# SOUTH, WEST
			return RNG.choice(["N", "E"])

	elif bx_mid > x_mid:
		if bz_mid <= z_mid:
			# return NORTH, EAST
			return RNG.choice(["S", "W"])
		elif bz_mid > z_mid:
			# return NORTH, WEST
			return RNG.choice(["N", "W"])
	return None


# def generateWindow_z(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

# 	window_height = h_max - int((h_max - h_min)/1.5)
# 	whmin = h_max - int((h_max - h_min)/1.5)
# 	whmax = h_max - int((h_max - h_min)/2.5)

# 	width = x_max - x_min
# 	pos_min = RNG.randint(x_min+int(width*0.1),x_min+int(width*0.4))
# 	pos_max= RNG.randint(x_min+int(width*0.6),x_min+int(width*0.9))

# 	for p in range(pos_min, pos_max):
# 		for w in range(whmin, whmax):
# 			matrix.setValue(w, p, z_min, (20,0))

# 	width = x_max - x_min
# 	pos_min = RNG.randint(x_min+int(width*0.1),x_min+int(width*0.4))
# 	pos_max= RNG.randint(x_min+int(width*0.6),x_min+int(width*0.9))

# 	for p in range(pos_min, pos_max):
# 		for w in range(whmin, whmax):
# 			matrix.setValue(w, p, z_max, (20,0))

# def generateWindow_x(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

# 	window_height = h_max - int((h_max - h_min)/1.5)
# 	whmin = h_max - int((h_max - h_min)/1.5)
# 	whmax = h_max - int((h_max - h_min)/2.5)

# 	width = z_max - z_min
# 	pos_min = RNG.randint(z_min+int(width*0.1),z_min+int(width*0.4))
# 	pos_max = RNG.randint(z_min+int(width*0.6),z_min+int(width*0.9))

# 	for p in range(pos_min, pos_max):
# 		for w in range(whmin, whmax):
# 			matrix.setValue(w, x_min, p, (20,0))

# 	width = z_max - z_min
# 	pos_min = RNG.randint(z_min+int(width*0.1),z_min+int(width*0.4))
# 	pos_max = RNG.randint(z_min+int(width*0.6),z_min+int(width*0.9))

# 	for p in range(pos_min, pos_max):
# 		for w in range(whmin, whmax):
# 			matrix.setValue(w, x_max, p, (20,0))


