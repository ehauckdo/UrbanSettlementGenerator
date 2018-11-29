from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random

inputs = (
	("Mountain Generator", "label"),
	("Top", alphaMaterials.Grass),
	("Filling", alphaMaterials.Dirt),
	)

def perform(level, box, options):
	generateMountainsCA(level,box,options)
	return

def generateMountainsCA(level, box, options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = executeCA(width,depth,height,options)

	w = width-1
	h = height-1
	d = depth -1

	for y in range(box.maxy, box.miny, -1):
		for x in range(box.maxx, box.minx, -1):
			for z in range(box.maxz, box.minz, -1):
				if matrix[h][w][d] is not 0:
					utilityFunctions.setBlock(level, (matrix[h][w][d], 0), x, y, z)
				d = d - 1
			w = w - 1
			d = depth - 1
		w = width-1
		h = h - 1
	return

# top-down implementation, so far the best result!
def executeCA(width, depth, height, options):
	matrix = [[[0 for z in range(depth)] for x in range(width)] for y in range(height)]

	xpeak = width/2
	zpeak = depth/2
	# fill the peak with some blocks
	matrix[height-1][xpeak][zpeak] = options["Top"].ID
	updateSides(matrix,width,depth,height-1,xpeak,zpeak,1,options["Top"].ID)
	updateDiagonals(matrix,width,depth,height-1,xpeak,zpeak,0.5,options["Top"].ID)

	# how many times execute CA in h-1 level
	generations = 5

	prevh = height-1
	for h in range(height-2,-1,-1):
		cells = findCells(matrix[prevh], width, depth)
		for x, y in cells:
			matrix[h][x][y] = options["Filling"].ID
		for gen in range(generations):
			cells = findCells(matrix[h], width, depth)
			for x, y in cells:
				updateSides(matrix,width,depth,h,x,y,0.2,options["Top"].ID)
		generations += random.randint(1,4)
		prevh = h

		# if the width/depth box is already filled at the current Height
		# stop generating and bring all the mountain downwards to the ground
		if reachedBoxLimit(matrix,h):
			matrix = adjustMatrix(matrix,h)
			break

	return matrix

def updateSides(matrix,width,depth,h,x,y,p,m):

	if ((x+1 < width) and random.random() < p):
		matrix[h][x+1][y] = m
	if ((x-1 >= 0) and random.random() < p):
		matrix[h][x-1][y] = m
	if ((y-1 >= 0) and random.random() < p):
		matrix[h][x][y-1] = m
	if ((y+1 < depth) and random.random() < p):
		matrix[h][x][y+1] = m

def updateDiagonals(matrix,width,depth,h,x,y,p,m):

	if ((x+1 < width) and (y+1 < depth) and random.random() < p):
		matrix[h][x+1][y+1] = m
	if ((x+1 < width) and (y-1 >= 0) and random.random() < p):
		matrix[h][x+1][y-1] = m
	if ((x-1 >= 0) and (y+1 < depth) and random.random() < p):
		matrix[h][x-1][y+1] = m
	if ((x-1 >= 0) and (y-1 >= 0) and random.random() < p):
		matrix[h][x-1][y-1] = m

def updateUpper(matrix,h,x,y,p,m):
	if (random.random() < p):
		matrix[h+1][x][y] = m

def findCells(matrix, w, d):
	cells = []
	for x in range(w):
		for y in range(d):
			if matrix[x][y] != 0:
				cells.append( (x,y))
	return cells

def adjustMatrix(matrix, h):
	drop = h

	for top_height in range(h, len(matrix)):
		for current_h in range(top_height, top_height-drop, -1):
			for x in range(len(matrix[current_h])):
				for z in range(len(matrix[current_h][x])):
					matrix[current_h-1][x][z]= matrix[current_h][x][z]
					matrix[current_h][x][z] = 0
	return matrix

def reachedBoxLimit(matrix, h):
	size = 0
	for i in range(len(matrix[h])):
		size += len(matrix[h][i])

	total = 0
	for x in range(len(matrix[h])):
		for z in range(len(matrix[h][x])):
			if matrix[h][x][z] != 0:
				total += 1
	print("SIZE: ", size)
	print("FILLED: ", total)

	if total > size * 0.85:
		print("THRESHOLD!")
		return True
	else:
		return False

def printBoxInfo(box):
	print("Printing Box Info: ")
	print("x_max: "+str(box.maxx)+ ", y_max: "+str(box.maxy)+ ", z_max: "+str(box.maxz))
	print("x_min: "+str(box.minx)+ ", y_min: "+str(box.miny)+ ", z_min: "+str(box.minz))
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	print("Width: "+str(width)+", Height: "+str(height)+", Depth: "+str(depth))
