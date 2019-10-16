import logging

air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
ground_like = [1, 2, 3]
water_like = [8, 9, 10, 11]

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
		h = matrix.getMatrixY(h)

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
		h = matrix.getMatrixY(h)

		next_block = path[i+1]
		next_h = height_map[next_block[0]][next_block[1]]
		next_h = matrix.getMatrixY(next_h)

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