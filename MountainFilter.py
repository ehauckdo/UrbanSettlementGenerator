from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random

inputs = (
	("Mountain Generator", "label"),
	("Material", alphaMaterials.Cobblestone),
	)

def perform(level, box, options):
	generateMountainsCA(level,box,options)
	return

def generateMountainsCA(level, box, options):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = executeCA(width,depth,height)

	w = width-1
	h = height-1
	d = depth -1

	for y in range(box.maxy, box.miny, -1):
		for x in range(box.maxx, box.minx, -1):
			for z in range(box.maxz, box.minz, -1):
				if matrix[h][w][d] is 1:
					utilityFunctions.setBlock(level, (options["Material"].ID, 0), x, y, z)
				d = d - 1
			w = w - 1
			d = depth - 1
		w = width-1
		h = h - 1
	return

def executeCA(width, depth, height):
	matrix = [[[0 for z in range(depth)] for x in range(width)] for y in range(height)]

	matrix = thirdImplementationCA(matrix,width,depth,height)

	return matrix

# top-down implementation, so far the best result!
def thirdImplementationCA(matrix, width, depth, height):

	xpeak = width/2
	zpeak = depth/2
	# fill the peak with some blocks
	matrix[height-1][xpeak][zpeak] = 1
	updateSides(matrix,width,depth,height-1,xpeak,zpeak,1)

	# how many times execute CA in h-1 level
	generations = 5

	prevh = height-1
	for h in range(height-2,-1,-1):
		cells = findCells(matrix[prevh], width, depth)
		for x, y in cells:
			matrix[h][x][y] = 1
		for gen in range(generations):
			cells = findCells(matrix[h], width, depth)
			for x, y in cells:
				updateSides(matrix,width,depth,h,x,y,0.2)
		generations += 1
		prevh = h

	return matrix

def updateSides(matrix,width,depth,h,x,y,p):

	if ((x+1 < width) and random.random() < p):
		matrix[h][x+1][y] = 1
	if ((x-1 >= 0) and random.random() < p):
		matrix[h][x-1][y] = 1
	if ((y-1 >= 0) and random.random() < p):
		matrix[h][x][y-1] = 1
	if ((y+1 < depth) and random.random() < p):
		matrix[h][x][y+1] = 1

def updateUpper(matrix,h,x,y,p):
	if (random.random() < p):
		matrix[h+1][x][y] = 1

def findCells(matrix, w, d):
	cells = []
	for x in range(w):
		for y in range(d):
			if matrix[x][y] == 2 or matrix[x][y] == 1:
				cells.append( (x,y))
	return cells

def printBoxInfo(box):
	print("Printing Box Info: ")
	print("x_max: "+str(box.maxx)+ ", y_max: "+str(box.maxy)+ ", z_max: "+str(box.maxz))
	print("x_min: "+str(box.minx)+ ", y_min: "+str(box.miny)+ ", z_min: "+str(box.minz))
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	print("Width: "+str(width)+", Height: "+str(height)+", Depth: "+str(depth))
