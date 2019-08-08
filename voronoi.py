import logging
import utilityFunctions as utilityFunctions
from Earthworks import prepareLot
import GenerateHouse 
from Voronoi import get_voronoi, get_random_points, print_voronoi, get_spaced_points

def perform(level, box, options):

	print("BoundingBox coordinates: ({},{}),({},{}),({},{})".format(box.miny, box.maxy, box.minx, box.maxx, box.minz, box.maxz))

	(width, height, depth) = utilityFunctions.getBoxSize(box)
	print("Selection box dimensions {}, {}, {}".format(width,height,depth))

	world = utilityFunctions.generateMatrix(level, box, width,depth,height)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})
	height_map = utilityFunctions.getHeightMap(level,box)

	partition = (0, height, 0, width, 0, depth)

	center, neighbourhoods = generateCenterAndNeighbourhood(world_space, height_map)

	points = []
	center_x = int((center[2] + center[3])/2)
	center_z = int((center[4] + center[5])/2)
	center_point = (center_x, center_z, 0)
	points.append(center_point)

	for n in neighbourhoods:
		points.extend(get_random_points(n[2], n[3], n[4], n[5], 2))

	print("POINTS: ")
	for p in points:
		print(p)

	n_pts = 5
	# points = get_random_points(0, width, 0, depth, n_pts-1)
	# points.append((int(width/2), int(depth/2), 5))

	voronoi = get_voronoi(points, width, depth)
	print_voronoi(voronoi, width, depth)

	lots = []
	center = None
	for p in points:
		rect = biggest_rectangle(voronoi, width, depth, p[2])
		lot = (0, height, rect[0], rect[1], rect[2], rect[3], p[2])
		if p != center_point:
			add_grass(world, height_map, voronoi, width, depth, p[2])
			lots.append(lot)
		else:
			center = lot

	print_voronoi(voronoi, width, depth)

	#paint_world(world, height_map, partition, voronoi)

	print("LOTS: ")
	for l in lots:
		print(l)
	print("CENTER: ")
	print(center)

	houses = []
	for l in lots:
		houses.append(generateHouse(world, l, height_map))
		add_fence(world, height_map, voronoi, width, depth, l[6])

	#generate_center(world, height_map, center)
	center_x = int((center[3] + center[2])/2)
	center_z = int((center[5] + center[4])/2)
	center_y = height_map[center_x][center_z]

	world.setValue(height_map[center_x][center_z]+1, center_x, center_z, (41,0))

	pathMap = utilityFunctions.getPathMap(height_map, width, depth)

	# Connecting houses to center
	pavementBlockID = 43
	pavementBlockSubtype = 8
	for h in houses:
		path = utilityFunctions.aStar(h.entranceLot, (center_y, center_x, center_z), pathMap, height_map)

		if path != None:
	 		print("Found path between {} and {}. Generating road...".format(h,  (center_y, center_x, center_z)))
		 	utilityFunctions.pavementConnection(world, path, height_map, (pavementBlockID, pavementBlockSubtype))

	change_ground_tile(world, height_map, voronoi, width, depth, 0, (43,8), (43,0))

	world.updateWorld()

def biggest_rectangle(voronoi, width, depth, color):
	x_max = z_max = -99999
	x_min = z_min = 99999
	print(width, depth)
	for x in range(width):
		for z in range(depth):
			if voronoi[x][z] == color:
				if x > x_max: x_max = x
				if x < x_min: x_min = x
				if z > z_max: z_max = z
				if z < z_min: z_min = z
	print(x_min, x_max, z_min, z_max)

	def is_valid(voronoi, x_min, x_max, z_min, z_max, color):
		for x in x_min, x_max:
			for z in z_min, z_max:
				if voronoi[x][z] != color:
					return False
		return True

	def generate_rectangle(x_min, x_max, z_min, z_max):
		from random import randrange
		new_x_min = randrange(x_min, x_max)
		new_x_max = randrange(new_x_min+1, x_max+1)
		new_z_min = randrange(z_min, z_max)
		new_z_max = randrange(new_z_min, z_max+1)
		area = (new_x_max - new_x_min) * (new_z_max - new_z_min)
		return (area, new_x_min, new_x_max, new_z_min, new_z_max)

	print(is_valid(voronoi, x_min, x_max, z_min, z_max, color))
	lots = []
	for i in range(1000):
		area, r_x_min, r_x_max, r_z_min, r_z_max = generate_rectangle(x_min, x_max, z_min, z_max)
		#print("Generated rectangle: ", (area, r_x_min, r_x_max, r_z_min, r_z_max))
		if is_valid(voronoi, r_x_min, r_x_max, r_z_min, r_z_max, color):
			lots.append((area, r_x_min, r_x_max, r_z_min, r_z_max))
	
	print("Total valid lots: {}".format(len(lots)))
	for l in reversed(sorted(lots)):
		print(l)
		area, r_x_min, r_x_max, r_z_min, r_z_max = l
		return (r_x_min, r_x_max, r_z_min, r_z_max)

def paint_world(world, height_map, p, voronoi):

	for x in range (p[2], p[3]):
		for z in range(p[4], p[5]):
			world.setValue(height_map[x][z], x, z, (35, voronoi[x][z]))
	

def generate_center(world, height_map, p):
	for x in range (p[2], p[3]):
		for z in range(p[4], p[5]):
			world.setValue(height_map[x][z], x, z, (43,8))

def change_ground_tile(world, height_map, voronoi, width, depth, color, block, edge_block):
	for x in range(width):
		for z in range(depth):
			if voronoi[x][z] == color:
				l = is_color(voronoi, x-1, z, color)
				r = is_color(voronoi, x+1, z, color)
				t = is_color(voronoi, x, z+1, color)
				b = is_color(voronoi, x, z-1, color)
				l_t = is_color(voronoi, x-1, z+1, color)
				r_t = is_color(voronoi, x+1, z+1, color)
				l_b = is_color(voronoi, x-1, z-1, color)
				r_b = is_color(voronoi, x+1, z-1, color)
				if l and r and t and b and l_t and r_t and l_b and r_b:
					world.setValue(height_map[x][z], x, z, block)
				else:
					world.setValue(height_map[x][z], x, z, edge_block)

def add_fence(world, height_map, voronoi, width, depth, color):
	for x in range(width):
		for z in range(depth):
			if voronoi[x][z] == color:
				is_edge = False
				#world.setValue(height_map[x][z], x, z, (2,0))
				l = is_color(voronoi, x-1, z, color)
				r = is_color(voronoi, x+1, z, color)
				t = is_color(voronoi, x, z+1, color)
				b = is_color(voronoi, x, z-1, color)
				l_t = is_color(voronoi, x-1, z+1, color)
				r_t = is_color(voronoi, x+1, z+1, color)
				l_b = is_color(voronoi, x-1, z-1, color)
				r_b = is_color(voronoi, x+1, z-1, color)
				if l and r and t and b and l_t and r_t and l_b and r_b:
					pass
				else:
					world.setValue(height_map[x][z]+1, x, z, (85,0))

def add_grass(world, height_map, voronoi, width, depth, color):
	for x in range(width):
		for z in range(depth):
			if voronoi[x][z] == color:
				world.setValue(height_map[x][z], x, z, (2,0))

def is_color(matrix, x, z, color):
	try:
		if matrix[x][z] == color:
			return True
	except:
		return False
	return False

def generateHouse(matrix, p, height_map):
	logging.info("Generating a house in lot {}".format(p))
	logging.info("Terrain before flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)
				
	h = prepareLot(matrix, p, height_map)

	logging.info("Terrain after flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)

	house = GenerateHouse.generateHouse(matrix, height_map[0][0], p[1],p[2],p[3], p[4], p[5])
	
	b = house.buildArea
	utilityFunctions.updateHeightMap(height_map, b.x_min, b.x_max, b.z_min, b.z_max, -1)

	logging.info("Terrain after construction: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)

	return house

def generateCenterAndNeighbourhood(space, height_map):
	neighbourhoods = []
	logging.info("Generating Neighbourhood Partitioning...")
	center = utilityFunctions.getSubsection(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.6)
	logging.info("Generated city center: {}".format(center))
	partitions = utilityFunctions.subtractPartition((space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max), center)
	for p in partitions:
		neighbourhoods.append(p)
		logging.info("Generated neighbourhood: {}".format(p))
	return (center, neighbourhoods)