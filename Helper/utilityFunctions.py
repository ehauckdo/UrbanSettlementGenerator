import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
from collections import defaultdict
from AStar import aStar
from Matrix import Matrix
import RNG
from copy import deepcopy
import sys

air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
ground_like = [1, 2, 3]
water_like = [8, 9, 10, 11]

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
def findTerrain_old(level, x, z, miny, maxy):
	blocks = []
	for y in xrange(miny, maxy):
		#print("y: ", y, " block: ", level.blockAt(x, y, z))
		if level.blockAt(x, y, z) == 0:
			return y-1
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

# Given an x an z coordinate, this will drill down a y column from box.maxy until box.miny and return a list of blocks
def drillDown(level,box):
	(width, height, depth) = getBoxSize(box)
	blocks = []
	for y in xrange(maxy, miny, -1):
		blocks.append(level.blockAt(x, y, z))
		# print level.blockAt(x,y,z)
	return blocks

# Given an x an z coordinate, this will go from box.miny to maxy and return the first block under an air block
def findTerrain(level, x, z, miny, maxy):
	

	blocks = []
	for y in xrange(maxy-1, miny-1, -1):
		#print("y: ", y, " block: ", level.blockAt(x, y, z))
		if level.blockAt(x, y, z) in air_like:
			continue
		elif level.blockAt(x, y, z) in water_like:
			return -1
		else:
			return y
		#elif level.blockAt(x, y, z) in ground_like:
		#	return y
		# print level.blockAt(x,y,z)
	return -1


# class that allows easy indexing of dicts
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    #__getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self.get(attr, None)

# generate and return 3d matrix as in the format matrix[h][w][d] 
def generateMatrix(level, box, width, depth, height):
	matrix = Matrix(level, box, height, width, depth)			
	return matrix

# get a subsection of a give arean partition based on the percentage
def getSubsection(y_min, y_max, x_min, x_max, z_min, z_max, percentage=0.8):

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

	return (y_min, y_max, subsection_x_min, subsection_x_max, subsection_z_min, subsection_z_max)

# remove inner partition from outer and return 4 partitions as the result
def subtractPartition(outer, inner):

	p1 = (outer[0], outer[1], outer[2], inner[2], outer[4], inner[5])
	p2 = (outer[0], outer[1], inner[2], outer[3], outer[4], inner[4])
	p3 = (outer[0], outer[1], inner[3], outer[3], inner[4], outer[5])
	p4 = (outer[0], outer[1], outer[2], inner[3], inner[5], outer[5])

	return (p1,p2,p3,p4)

def getEuclidianDistancePartitions(p1, p2):
	
	p1_center = (p1[0] + int((p1[1]-p1[0])*0.5), p1[2] + int((p1[3]-p1[2])*0.5))
	p2_center = (p2[0] + int((p2[1]-p2[0])*0.5), p2[2] + int((p2[3]-p2[2])*0.5))
	euclidian_distance = getEuclidianDistance(p1_center,p2_center)
	return euclidian_distance

def getEuclidianDistance(p1,p2):
	distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
	return distance

def getManhattanDistance(p1,p2):
	distance = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
	return distance


# Given a partition and height map, return true if there's no water
# or other unwalkable block inside that partition
def hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map):
	
	for x in range(x_min, x_max):
		for z in range(z_min, z_max):
			if height_map[x][z] == -1:
				return False
	return True

# Return true if a partition has the minimum size specified
def hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h=4, minimum_w=16, minimum_d=16):

	if y_max-y_min < minimum_h or x_max-x_min < minimum_w or z_max-z_min < minimum_d:
		return False
	return True

# Return true if a given partition has an acceptable steepness
# according to the a scoring function and a threshold
def hasAcceptableSteepness(x_min, x_max,z_min,z_max, height_map, scoring_function, threshold = 5):
	initial_value = height_map[x_min][z_min]
	score = scoring_function(height_map, x_min, x_max, z_min , z_max , initial_value)
	if score > threshold:
		return False
	return True

# given a box selection, returns a 2d matrix where each element is
# the height of the first non-block air in that x, z position
def getHeightMap(level, box):
	logging.info("Calculating height map...")
	terrain = [[0 for z in range(box.minz,box.maxz)] for x in range(box.minx,box.maxx)]
	
	for d, z in zip(range(box.minz,box.maxz), range(0, box.maxz-box.minz)):
		for w, x in zip(range(box.minx,box.maxx), range(0, box.maxx-box.minx)):
			terrain[x][z] = findTerrain(level, w, d, box.miny, box.maxy)

	#print("Terrain Map: ")
	#for x in range(0, box.maxx-box.minx):
	#	print(terrain[x])
	return terrain

def getPathMap(height_map, width, depth):
	pathMap = []

	print(width, depth)
	for x in range(width):
		pathMap.append([])
		for z in range(depth):
			pathMap[x].append(dotdict())

	threshold = 50
	for x in range(width):
		for z in range(depth):

			#left
			if x-1 < 0:
				pathMap[x][z].left = -1
			else:
				pathMap[x][z].left = abs(height_map[x-1][z] - height_map[x][z])
				if pathMap[x][z].left > threshold or height_map[x-1][z] == -1:
					pathMap[x][z].left = -1


			#right
			if x+1 >= width:
				pathMap[x][z].right = -1
			else:
				pathMap[x][z].right = abs(height_map[x][z] - height_map[x+1][z])
				if pathMap[x][z].right > threshold or height_map[x+1][z] == -1:
					pathMap[x][z].right = -1

			#down 
			if z-1 < 0:
				pathMap[x][z].down = -1
			else:
				pathMap[x][z].down = abs(height_map[x][z] - height_map[x][z-1])
				if pathMap[x][z].down > threshold or height_map[x][z-1] == -1:
					pathMap[x][z].down = -1			

			#up 
			if z+1 >= depth:
				pathMap[x][z].up = -1
			else:
				pathMap[x][z].up = abs(height_map[x][z+1] - height_map[x][z])
				if pathMap[x][z].up > threshold or height_map[x][z+1] == -1:
					pathMap[x][z].up = -1
			
	return pathMap


def getScoreArea_type1(height_map, min_x, max_x, min_z, max_z, initial_value=None):
	if initial_value == None:
		initial_value = height_map[min_x][min_z]

	ocurred_values = []
	value = 0
	for x in range(min_x, max_x+1):
		for z in range(min_z, max_z+1):
			difference = initial_value - height_map[x][z]
			if difference not in ocurred_values:
				ocurred_values.append(difference)
  	return len(ocurred_values)

def getScoreArea_type2(height_map, min_x, max_x, min_z, max_z, initial_value=None):
	if initial_value == None:
		initial_value = height_map[min_x][min_z]

	value = 0
	for x in range(min_x, max_x+1):
		for z in range(min_z, max_z+1):
			value += abs(initial_value - height_map[x][z])
  	return value

def getScoreArea_type3(height_map, min_x, max_x, min_z, max_z, initial_value=None):
	if initial_value == None:
		initial_value = height_map[min_x][min_z]

	value = 0
	for x in range(min_x, max_x+1):
		for z in range(min_z, max_z+1):

			value += (abs(initial_value - height_map[x][z]))**2
  	return value

def getHeightCounts(matrix, min_x, max_x, min_z, max_z):
	flood_values = {}
	for x in range(min_x, max_x+1):
		for z in range(min_z, max_z+1):
			value = matrix[x][z]
			if value not in flood_values.keys():
				flood_values[value] = 1
			else:
				flood_values[value] += 1
	return flood_values

def getMostOcurredGroundBlock(matrix, height_map, min_x, max_x, min_z, max_z):
	block_values = {}
	for x in range(min_x, max_x+1):
		for z in range(min_z, max_z+1):
			groundBlock = matrix.getValue(height_map[x][z], x, z)
			if type(groundBlock) == tuple:
				groundBlock = groundBlock[0]
			if groundBlock not in block_values.keys():
				block_values[groundBlock] = 1
			else:
				block_values[groundBlock] += 1
	for key in sorted(block_values, key=block_values.get):
		if key not in air_like:
			return (key, 0)

	grass_block = (2,0)
	return grass_block


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

# returns whether or not 2 partitions are colliding, must be in the format
# (x_min, x_max, z_min, z_max)
def intersectPartitions(p1, p2):
    return not (p2[2] >= p1[3] or p2[3] <= p1[2] or p2[5] <= p1[4] or p2[4] >= p1[5])

def getNonIntersectingPartitions(partitioning):
	cleaned_partitioning = []
	for score, partition in partitioning:
		intersect = False
		for valid_partition in cleaned_partitioning:
			if intersectPartitions(partition, valid_partition):
				intersect = True
				break
		if intersect == False:
			cleaned_partitioning.append(partition) 
	return cleaned_partitioning

# update the minecraft world given a matrix with h,w,d dimensions, and each element in the
# (x, y) format, where x is the ID of the block and y the subtype
def updateWorld(level, box, matrix, height, width, depth):
	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix.isChanged(h,w,d):
					try:
						block = matrix.getValue(h,w,d)
						setBlock(level, (block[0], block[1]), x, y, z)
					except:
						block = matrix.getValue(h,w,d)
						setBlock(level, (block, 0), x, y, z)

def getCentralPoint(x_min, x_max, z_min, z_max):
	x_mid = x_max - int((x_max - x_min)/2)
	z_mid = z_max - int((z_max - z_min)/2)
	return (x_mid, z_mid)

def pavementConnection_StraightLine(matrix, x_p1, z_p1, x_p2, z_p2, height_map, pavementBlock = (4,0)):
	logging.info("Connecting {} and {}".format((x_p1, z_p1), (x_p2, z_p2)))
	for x in twoway_range(x_p1, x_p2):
		h = height_map[x][z_p1]
		matrix.setValue(h,x,z_p1,pavementBlock)
		
	for z in twoway_range(z_p1, z_p2):
		h = height_map[x_p2][z]
		matrix.setValue(h,x_p2,z, pavementBlock)
		matrix.setValue(h+1,x_p2,z, (0,0))

def getOrientation(x1, z1, x2, z2):
	if x1 < x2:   return "E"
	elif x1 > x2: return "W"
	elif z1 < z2: return "S"
	elif z1 > z2: return "N"
	else: return None

def pavementConnection(matrix, path, height_map, pavementBlock = (4,0), baseBlock=(2,0)):
	block = previous_block = path[0]
	x = block[0]
	z = block[1]
	
	def fillUnderneath(matrix, y, x, z, baseBlock):
		if y < 0: return
		block = matrix.getValue(y, x, z)
		if type(block) == tuple: block = block[0]
		if block in air_like or block in water_like:
			matrix.setValue(y, x, z, baseBlock)
			logging.info("(fillUnderneath) Block: {}, Filling.... Moving to height {}".format(block, y-1))
			fillUnderneath(matrix, y-1, x, z, baseBlock)
		#else:
			#logging.info("Finished underneath filling at {}".format(y))

	def fillAbove(matrix, y, x, z, up_to):
		if up_to < 0 or y >= matrix.height: return
		block = matrix.getValue(y, x, z)
		if type(block) == tuple: block = block[0]
		if block in air_like:
			matrix.setValue(y,x,z, (0,0))
		fillAbove(matrix, y+1, x, z, up_to-1)

	# logging.info("Path before:")
	# for p in path:
	# 	logging.info(p)
	# path = path[::-1]
	# logging.info("Path after:")
	# for p in path:
	# 	logging.info(p)

	for i in range(0, len(path)-1):

		block = path[i]
		x = block[0]
		z = block[1]
		h = height_map[x][z]

		matrix.setValue(h,x,z,pavementBlock)
		fillUnderneath(matrix, h-1, x, z, pavementBlock)
		fillAbove(matrix, h+1, x, z, 5)

		next_block = path[i+1]
		next_h = height_map[next_block[0]][next_block[1]]

		logging.info("Generating road at point {}, {}, {}".format(h, x, z))
		logging.info("next_h: {}".format(next_h))
		
		# check if we are moving in the x axis (so to add a new pavement
		# on the z-1, z+1 block)
		if x != next_block[0]:

			# if that side block is walkable
			if z-1 >= 0 and height_map[x][z-1] != -1: 
				matrix.setValue(h,x,z-1,pavementBlock)
				# try to fill with earth underneath if it's empty
				#logging.info("Filling underneath at height {}".format(h-1))
				fillUnderneath(matrix, h-1, x, z-1, pavementBlock)
				# fill upwards with air to remove any obstacles
				fillAbove(matrix, h+1, x, z-1, 5)

			# if the opposite side block is walkable
			if z+1 < matrix.depth and height_map[x][z+1] != -1:
				matrix.setValue(h,x,z+1,pavementBlock)
				#logging.info("Filling underneath at height {}".format(h-1))
				fillUnderneath(matrix, h-1, x, z+1, pavementBlock)
				fillAbove(matrix, h+1, x, z+1, 5)

		elif z != next_block[1]:
			# check if we are moving in the z axis (so add a new pavement
			# on the x-1 block) and if that side block is walkable
			if x-1 >= 0 and height_map[x-1][z] != -1:
				matrix.setValue(h,x-1,z,pavementBlock)
				#logging.info("Filling underneath at height {}".format(h-1))
				fillUnderneath(matrix, h-1, x-1, z, pavementBlock)
				fillAbove(matrix, h+1, x-1, z, 5)


			if x+1 < matrix.width and height_map[x+1][z] != -1:
				matrix.setValue(h,x+1,z,pavementBlock)
				#logging.info("Filling underneath at height {}".format(h-1))
				fillUnderneath(matrix, h-1, x+1, z, pavementBlock)
				fillAbove(matrix, h+1, x+1, z, 5)

	# another iteration over the path to generate ladders
	# this is to guarantee that fillAbove or any other
	# manipulations of the environment around the path
	# will erase the ladder blocks
	for i in range(0, len(path)-1):

		block = path[i]
		x = block[0]
		z = block[1]
		#h = 100
		h = height_map[x][z]

		next_block = path[i+1]
		next_h = height_map[next_block[0]][next_block[1]]

		orientation = getOrientation(x, z, next_block[0], next_block[1])
		if abs(h-next_h) > 1:
			if h < next_h:
				if orientation == "N":   stair_subID = 3
				elif orientation == "S": stair_subID = 2
				elif orientation == "E": stair_subID = 4
				elif orientation == "W": stair_subID = 5
				for ladder_h in range(h+1, next_h+1):
					matrix.setValue(ladder_h, x, z,(65,stair_subID))
					# make sure that the ladders in which the stairs are attached
					# are cobblestone and not dirt, etc
					matrix.setValue(ladder_h, next_block[0], next_block[1], (pavementBlock))
			elif h > next_h:
				if orientation == "N":   stair_subID = 2
				elif orientation == "S": stair_subID = 3
				elif orientation == "E": stair_subID = 5
				elif orientation == "W": stair_subID = 4
				for ladder_h in range(next_h+1, h+1):
					matrix.setValue(ladder_h, next_block[0], next_block[1], (65,stair_subID))
					# make sure that the ladders in which the stairs are attached
					# are cobblestone and not dirt, etc
					matrix.setValue(ladder_h, x, z, (pavementBlock))

def getMST_Manhattan(buildings, pathMap, height_map):
	MST = []
	vertices = []
	partitions = deepcopy(buildings)

	selected_vertex = partitions[RNG.randint(0, len(partitions)-1)]
	logging.info("Initial selected partition: {}".format(selected_vertex))
	vertices.append(selected_vertex)
	partitions.remove(selected_vertex)

	while len(partitions) > 0:
	
		edges = []
		for v in vertices:
			logging.info("v: {}".format(v))
			for p in partitions:
				logging.info("\tp: {}".format(p))				
				p1 = v.entranceLot
				p2 = p.entranceLot
				distance = getManhattanDistance((p1[1],p1[2]), (p2[1],p2[2]))	
				edges.append((distance, v, p))

		edges = sorted(edges)
		if len(edges) > 0:
			MST.append((edges[0][0], edges[0][1], edges[0][2]))
		partitions.remove(edges[0][2])
		vertices.append(edges[0][2])
	return MST
	

#print a matrix given its h,w,d dimensions
def printMatrix(matrix, height, width, depth):
	for h in range(0,height):
		print("matrix at height: ", h)
		for x in range(0,width):
			print(matrix[h][x])

def twoway_range(start, stop):
	return range(start, stop+1, 1) if (start <= stop) else range(start, stop-1, -1)

def updateHeightMap(height_map, x_min, x_max, z_min, z_max, height):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			height_map[x][z] = height

def cleanProperty(matrix, h_min, h_max, x_min, x_max, z_min, z_max):
	for h in range(h_min, h_max):
		for x in range(x_min, x_max+1):
			for z in range(z_min, z_max+1):
				matrix.setValue(h,x,z, (0,0))

# algorithm to randomly find flat areas given a height map
def getAreasSameHeight(box,terrain):
	validAreas = []

	for i in range(0, 1000):
		random_x = RNG.randint(0, box.maxx-box.minx)
		random_z = RNG.randint(0,box.maxz-box.minz)
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

def checkSameHeight(terrain, minx, maxx, minz, maxz, random_x, random_z, mininum_w, mininum_d):
	if random_x + mininum_w > maxx or random_z + mininum_d > maxz or terrain[random_x][random_z] == -1:
		return False

	initial_value = terrain[random_x][random_z]

	for x in range(random_x, random_x + mininum_w):
		for z in range(random_z, random_z + mininum_d):
			#print("Checking x, z: ", x, z)
			if terrain[x][z] != initial_value:
				return False

	return True
