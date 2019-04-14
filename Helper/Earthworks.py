import utilityFunctions
import logging

# Perform earthworks on a given lot, returns the height to start construction
def prepareLot(matrix, p, height_map):

	areaScore = utilityFunctions.getScoreArea_type1(height_map, p[2],p[3], p[4], p[5], height_map[p[2]][p[4]])
	logging.info("Preparing lot {} with score {}".format(p, areaScore))

	if areaScore != 0:
		terrain_height = flattenPartition(matrix, p[2],p[3], p[4], p[5], height_map)
		logging.info("Terrain was flattened at height {}".format(terrain_height))
		utilityFunctions.updateHeightMap(height_map, p[2], p[3], p[4], p[5], terrain_height)
		h = matrix.getMatrixY(terrain_height)
	else:
		heightCounts = utilityFunctions.getHeightCounts(height_map, p[2],p[3], p[4], p[5])
		terrain_height = max(heightCounts, key=heightCounts.get)
		logging.info("No changes in terrain were necessary, terrain at height {}".format(terrain_height))
		utilityFunctions.updateHeightMap(height_map, p[2], p[3], p[4], p[5], terrain_height)
		# update the ground with the grass block
		for x in range(x_min, x_max):
			for z in range(z_min,z_max):
				matrix.setValue(terrain_height, x, z, (2,0))
		h = matrix.getMatrixY(terrain_height)
		

	logging.info("Index of height {} in selection box matrix: {}".format(terrain_height, h))

	return h

# Given the map matrix, a partition (x_min, x_max, z_min, z_max) and a
# height_map, perform earthworks on this lot by the flattening
# returns the height in which construction should start
def flattenPartition(matrix, x_min, x_max, z_min, z_max, height_map):

	heightCounts = utilityFunctions.getHeightCounts(height_map, x_min, x_max, z_min, z_max)
	most_ocurred_height = max(heightCounts, key=heightCounts.get)

	logging.info("Flattening {}".format((x_min, x_max, z_min, z_max)))

	base_block = utilityFunctions.getMostOcurredGroundBlock(matrix, height_map, x_min, x_max, z_min, z_max)
	logging.info("Most occurred ground block: {}".format(base_block))
	base_block = (2,0)
	logging.info("Flattening at height {}".format(most_ocurred_height))

	for x in range(x_min, x_max):
		for z in range(z_min,z_max):
			if height_map[x][z] == most_ocurred_height:
				# Equal height! No flattening needed
				# but lets use the base block just in case
				matrix.setValue(height_map[x][z], x, z, base_block)
			if height_map[x][z] != most_ocurred_height:

				if height_map[x][z] == -1:
					logging.warning("Flattening invalid area. Position ", x, z, " of height_map is -1. Cannot do earthworks.")
					continue

				matrix_height = matrix.getMatrixY(height_map[x][z])
				desired_matrix_height = matrix.getMatrixY(most_ocurred_height)

				if desired_matrix_height > matrix_height:
					for y in range(matrix_height, desired_matrix_height+1):
						matrix.setValue(y,x,z, base_block)
				else:
					#update every block between top height and the desired height
					# when bringing the ground to a lower level, this will have the 
					# effect of e.g. erasing trees that were on top of that block
					# this may cause some things to be unproperly erased
					# (e.g. a branch of a tree coming from an nearby block)
					# but this is probably the best/less complex solution for this
					for y in range(matrix.height-1, desired_matrix_height, -1):
						matrix.setValue(y,x,z, 0)
					matrix.setValue(desired_matrix_height,x,z, base_block)

	return most_ocurred_height