color_id = 1

def get_voronoi(points, width, height):
	voronoi = []
	print("creating a voronoi matrix of {}x{}".format(width, height))
	for x in range(width):
		column = []
		for y in range(height):
			column.append(-1)
		voronoi.append(column)

	for x in range(width):
		for y in range(height):
			#print("checking point ({},{})".format(x,y))
			closest_point = -1
			closest_distance = width * height

			for p in points:
				point_distance = dist(p[0], p[1], x , y)

				if point_distance < closest_distance:
					closest_distance = point_distance
					closest_point = p[2]
	
			voronoi[x][y] = closest_point

	return voronoi

def get_random_points(x_min, x_max, z_min, z_max, n_points):
	from random import randrange
	global color_id
	points = []
	for i in range(n_points):
		x = randrange(x_min, x_max*1)
		z = randrange(z_min, z_max+1)
		#print("Selected point: {},{}".format(x, y))
		points.append((x, z, color_id))
		color_id = color_id +  1
	return points

def get_spaced_points(width, height, n_points):
	points = []
	x_points = int(width / n_points)
	z_points = int(height / n_points)
	for x in range(x_points, width, x_points):
		for z in range(z_points, height, z_points):
			points.append((x, z, color_id))
			color_id += 1
	return points

def dist(x1, y1, x2, y2):
	import math
	dist = math.hypot(x1 - x2, y2 - y1)
	return dist

def print_voronoi(matrix, height, width):
	
	colors = {0:37, 1:31, 2:32, 3:33, 4:34, 5:35, 6:36}
	for x in range(len(matrix)):
		string = ""
		for y in range(len(matrix[x])):
			string += "\033[1;{};40m{:02d}".format(colors[matrix[x][y]%7], matrix[x][y])
		print(string)