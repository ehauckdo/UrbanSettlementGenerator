import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

# These are a few helpful functions we hope you find useful to use



# sets the block to the given blocktype at the designated x y z coordinate
# *params*
# level : the minecraft world level
# (block, data) : a tuple with block = the block id and data being a subtype
# x,y,z : the coordinate to set
def setBlock(level, (block, data), x, y, z):
	level.setBlockAt((int)(x),(int)(y),(int)(z), block)
    	level.setBlockDataAt((int)(x),(int)(y),(int)(z), data)

# sets the block to the given blocktype at the designated x y z coordinate IF the block is empty (air)
# *params*
# level : the minecraft world level
# (block, data) : a tuple with block = the block id and data being a subtype
# x,y,z : the coordinate to set
def setBlockIfEmpty(level, (block, data), x, y, z):
    tempBlock = level.blockAt((int)(x),(int)(y),(int)(z))
    if tempBlock == 0:
		setBlock(level, (block, data), (int)(x),(int)(y),(int)(z))

# sets every block to the given blocktype from the given x y z coordinate all the way down to ymin if the block is empty
# *params*
# level : the minecraft world level
# (block, data) : a tuple with block = the block id and data being a subtype
# x,y,z : the coordinate to set
# ymin: the minium y in which the iteration ceases
def setBlockToGround(level, (block, data), x, y, z, ymin):
    for iterY in xrange(ymin, (int)(y)):
    	setBlockIfEmpty(level, (block, data), (int)(x),(int)(iterY),(int)(z))


# Given an x an z coordinate, this will drill down a y column from box.maxy until box.miny and return a list of blocks
def drillDown(level, x, z, miny, maxy):
	blocks = []
	for y in xrange(maxy, miny, -1):
		blocks.append(level.blockAt(x, y, z))
		# print level.blockAt(x,y,z)
	return blocks

# Given an x an z coordinate, this will go from box.miny to maxy and return the first block under an air block
def findTerrain(level, x, z, miny, maxy):
	blocks = []
	for y in xrange(miny, maxy):
		#print("y: ", y, " block: ", level.blockAt(x, y, z))
		if level.blockAt(x, y, z) == 0:
			return y-1
		# print level.blockAt(x,y,z)
	return -1
	

# Given an x an z coordinate, this will go from box.miny to maxy and return the first block under an air block
def findTerrainNew(level, x, z, miny, maxy):
	air_like = [0, 6, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175]
	ground_like = [1, 2, 3]
	water_like = []

	blocks = []
	for y in xrange(maxy, miny-1, -1):
		#print("y: ", y, " block: ", level.blockAt(x, y, z))
		if level.blockAt(x, y, z) in air_like:
			continue
		else:
			return y
		#elif level.blockAt(x, y, z) in ground_like:
		#	return y
		# print level.blockAt(x,y,z)
	return -1

# returns a 2d matrix representing tree trunk locations on an x-z coordinate basis (bird's eye view) in the given box
# *params*
# level: the minecraft world level
# box: the selected subspace of the world
def treeMap(level, box):
	# Creates a 2d array containing z rows, each of x items, all set to 0
	w = abs(box.maxz - box.minz)
	h = abs(box.maxx - box.minx)
	treeMap = zeros((w,h))

	countx = box.minx
	countz = box.minz
	# iterate over the x dimenison of the mapping
	for x in range(h):
		# iterate over the z dimension of the mapping
		countz = box.minz
		for z in range(w):
			# drillDown at this location and get all the blocks in the y-column
			column = drillDown(level, countx, countz, box.miny, box.maxy)
			for block in column:
				# check if any block in this column is a wooden trunk block. If so, there is at this x-z coordinate
				if block == 17:
					treeMap[z][x] = 17
			print treeMap[z][x] ,
			countz += 1
		print ''
		countx += 1
	return treeMap


# returns the box size dimensions in x y and z
def getBoxSize(box):
	return (box.maxx - box.minx, box.maxy - box.miny, box.maxz - box.minz)

# returns an array of blocks after raytracing from (x1,y1,z1) to (x2,y2,z2)
# this uses Bresenham 3d algorithm, taken from a modified version written by Bob Pendleton  
def raytrace((x1, y1, z1), (x2, y2, z2)):
	output = []

	x2 -= 1
	y2 -= 1
	z2 -= 1

	i = 0
	dx = 0
	dy = 0
	dz = 0
	l = 0
	m = 0
	n = 0
	x_inc = 0
	y_inc = 0
	z_inc = 0
	err_1 = 0
	err_2 = 0
	dx2 = 0
	dy2 = 0
	dz2 = 0
	point = [x1,y1,z1]

	dx = x2 - x1
	dy = y2 - y1;
	dz = z2 - z1;
	x_inc = -1  if dx < 0 else 1
	l = abs(dx)
	y_inc = -1 if dy < 0 else 1
	m = abs(dy)
	z_inc = -1 if dz < 0 else 1
	n = abs(dz)
	dx2 = l << 1
	dy2 = m << 1
	dz2 = n << 1
    
	if l >= m and l >= n:
		err_1 = dy2 - l
		err_2 = dz2 - l
		for i in range(l):
			np = (point[0], point[1], point[2])
			output.append(np)
			if err_1 > 0:
				point[1] += y_inc
				err_1 -= dx2

			if err_2 > 0:
				point[2] += z_inc
				err_2 -= dx2

			err_1 += dy2
			err_2 += dz2
			point[0] += x_inc
        
	elif m >= l and m >= n:
		err_1 = dx2 - m
		err_2 = dz2 - m
		for i in range(m):
			np = (point[0], point[1], point[2])
			output.append(np)
			if err_1 > 0:
				point[0] += x_inc
				err_1 -= dy2

			if err_2 > 0:
				point[2] += z_inc
				err_2 -= dy2

			err_1 += dx2
			err_2 += dz2
			point[1] += y_inc
        
	else: 
		err_1 = dy2 - n
		err_2 = dx2 - n
		for i in range(n):
			np = (point[0], point[1], point[2])
			output.append(np)
			if err_1 > 0:
				point[1] += y_inc
				err_1 -= dz2

			if err_2 > 0:
				point[0] += x_inc
				err_2 -= dz2

			err_1 += dy2
			err_2 += dx2
			point[2] += z_inc

	np = (point[0], point[1], point[2])
	output.append(np)
	return output

# generate and return 3d matrix as in the format matrix[h][w][d] 
def generateMatrix(width, depth, height, options):
	matrix = [[[None for z in range(depth)] for x in range(width)] for y in range(height)]		
	return matrix

# get a subsection of a give arean partition based on the percentage
def getSubsection(x_min, x_max, z_min, z_max, percentage=0.8):

	width = x_max - x_min
	x_mid = x_min + int(width/2)

	subsection_x_size = int(width*percentage)
	subsection_x_mid = int(subsection_x_size/2)
	subsection_x_min = x_mid - subsection_x_mid
	subsection_x_max = x_mid + subsection_x_mid

	depth = z_max - z_min
	z_mid = z_min + int(depth/2)

	subsection_z_size = int(depth*percentage)
	subsection_z_mid = int(subsection_z_size/2)

	subsection_z_min = z_mid - subsection_z_mid
	subsection_z_max = z_mid + subsection_z_mid

	return (subsection_x_min, subsection_x_max, subsection_z_min, subsection_z_max)

# from a list of partitions in the format of (x_min, x_max, z_min, z_max)
# return the partition with the biggest area in the list
def getBiggestPartition(partitions):
	biggestArea = 0
	biggestPartition = None
	for p in partitions:
		width = p[1] - p[0]
		depth =  p[3] - p[2]
		area = width * depth
		print(area, width, depth)
		if area > biggestArea:
			biggestArea = area
			biggestPartition = p
	print(biggestArea)
	return biggestPartition

# subtract inner partition from outer and return 4 partitions as the result
def subtractPartition(outer, inner):
	print(outer,inner)

	p1 = (outer[0], inner[0], outer[2], inner[3])
	p2 = (inner[0], outer[1], outer[2], inner[2])
	p3 = (inner[1], outer[1], inner[2], outer[3])
	p4 = (outer[0], inner[1], inner[3], outer[3])

	print(p1)
	print(p2)
	print(p3)
	print(p4)

	return (p1,p2,p3,p4)


def getEuclidianDistancePartitions(p1, p2):
	
	p1_center = (p1[0] + int((p1[1]-p1[0])*0.5), p1[2] + int((p1[3]-p1[2])*0.5))
	p2_center = (p2[0] + int((p2[1]-p2[0])*0.5), p2[2] + int((p2[3]-p2[2])*0.5))
	print("EuclidianDistance: ")
	print(p1_center)
	print(p2_center)
	euclidian_distance = getEuclidianDistance(p1_center,p2_center)
	print(euclidian_distance)
	return euclidian_distance

def getEuclidianDistance(p1,p2):
	distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
	return distance


# Given an x an z coordinate, this will drill down a y column from box.maxy until box.miny and return a list of blocks
def drillDown(level,box):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	blocks = []
	for y in xrange(maxy, miny, -1):
		blocks.append(level.blockAt(x, y, z))
		# print level.blockAt(x,y,z)
	return blocks

# algorithm to randomly find flat areas given a height map
def getAreasSameHeight(box,terrain):
	validAreas = []

	for i in range(0, 1000):
		random_x = random.randint(0, box.maxx-box.minx)
		random_z = random.randint(0,box.maxz-box.minz)
		size_x = 15
		size_z = 15
		if checkSameHeight(terrain, 0, box.maxx-box.minx, 0,box.maxz-box.minz, random_x, random_z, size_x, size_z):
			newValidArea = (random_x, random_x+size_x-1, random_z, random_z+size_z-1)
			if newValidArea not in validAreas:
				validAreas.append(newValidArea)

	print("Valid areas found:")
	validAreas = removeOverlaping(validAreas)
	for a in validAreas:
		print(a)

	return validAreas

# given a box selection, returns a 2d matrix where each element is
# the height of the first non-block air in that x, z position
def getHeightMap(level, box):
	terrain = [[0 for z in range(box.minz,box.maxz)] for x in range(box.minx,box.maxx)]
	
	for d, z in zip(range(box.minz,box.maxz), range(0, box.maxz-box.minz)):
		for w, x in zip(range(box.minx,box.maxx), range(0, box.maxx-box.minx)):
			terrain[x][z] = findTerrainNew(level, w, d, box.miny, box.maxy)

	print("Terrain Map: ")
	for x in range(0, box.maxx-box.minx):
		print(terrain[x])

	return terrain

def checkSameHeight(terrain, minx, maxx, minz, maxz, random_x, random_z, mininum_w, mininum_d):
	# sample testing
	#print("Testing if valid area starting in ", random_x, random_z)
	#print("limits of matrix: ", minx, maxx, minz, maxz)

	if random_x + mininum_w > maxx or random_z + mininum_d > maxz or terrain[random_x][random_z] == -1:
		return False

	initial_value = terrain[random_x][random_z]

	for x in range(random_x, random_x + mininum_w):
		for z in range(random_z, random_z + mininum_d):
			#print("Checking x, z: ", x, z)
			if terrain[x][z] != initial_value:
				return False

	return True

# receives a list of areas in the format (x_min, x_max, z_min, z_max)
# returns the same list minus any overlaping areas
def removeOverlaping(areas):
	if len(areas) == 0: return areas

	# get the first area from the list as a valid area
	validAreas = areas[:1]
	areas = areas[1:]

	for i in range(len(areas)):
		current_area = areas[0]
		for index, a in enumerate(validAreas):
			if intersectRect(current_area, a):
				break 
		else:
			validAreas.append(current_area)
		areas = areas[1:]

	return validAreas

# returns whether or not 2 partitions are colliding, must be in the format
# (x_min, x_max, z_min, z_max)
def intersectRect(p1, p2):
    return not (p2[0] >= p1[1] or p2[1] <= p1[0] or p2[3] <= p1[2] or p2[2] >= p1[3])

# update the minecraft world given a matrix with h,w,d dimensions, and each element in the
# (x, y) format, where x is the ID of the block and y the subtype
def updateWorld(level, box, matrix, height, width, depth):
	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != None:
					setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

#print a matrix given its h,w,d dimensions
def printMatrix(matrix, height, width, depth):
	for h in range(0,height):
		print("matrix at height: ", h)
		for x in range(0,width):
			print(matrix[h][x])

