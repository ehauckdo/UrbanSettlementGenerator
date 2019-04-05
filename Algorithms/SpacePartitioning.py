import random
import logging
import RNG

def binarySpacePartitioning(y_init, y_end, x_init, x_end, d_init, d_end, partitions, partition_min=30, valid_min=15):

	split_horizontal = False
	split_vertical = False

	#logging.info("binarySpacePartitioning params: ", y_init, y_end, x_init, x_end, d_init, d_end, partitions, partition_min, valid_min)
	
	if x_end - x_init > partition_min and d_end - d_init > partition_min:
		if RNG.choice([True, False]): split_horizontal = True
		else: split_vertical = True
	elif x_end - x_init > partition_min:
		split_horizontal = True
	elif d_end - d_init > partition_min:
		split_vertical = True
	else:
		if x_end - x_init > valid_min and d_end - d_init > valid_min:
			partitions.append((y_init, y_end, x_init, x_end, d_init, d_end))

	if split_horizontal:
		#logging.info("split_horizontal", random.randint(x_init, x_end))
		x_mid = RNG.randint(x_init, x_end)
		binarySpacePartitioning(y_init, y_end, x_init, x_mid, d_init, d_end, partitions, partition_min, valid_min)
		binarySpacePartitioning(y_init, y_end, x_mid+1, x_end, d_init, d_end, partitions, partition_min, valid_min)
		
	elif split_vertical:
		#logging.info("split_vertical", random.randint(d_init, d_end))
		d_mid = RNG.randint(d_init, d_end)
		binarySpacePartitioning(y_init, y_end, x_init, x_end, d_init, d_mid, partitions, partition_min, valid_min)
		binarySpacePartitioning(y_init, y_end, x_init, x_end, d_mid+1, d_end, partitions, partition_min, valid_min)

	return partitions


def quadtreeSpacePartitioning(y_init, y_end, x_init, x_end, z_init, z_end, partitions=[], stop_chance=0, partition_min=25):

	if RNG.random() < stop_chance:
		#logging.info("Stopping at level ", stop_chance)
		partitions.append((y_init, y_end, x_init, x_end, z_init, z_end))
		return partitions

	width = x_end - x_init
	depth = z_end - z_init
	stop_chance += 0.05

	min_wrange = width/partition_min
	min_drange = depth/partition_min

	if min_wrange < 2 and min_drange < 2:
		partitions.append((y_init, y_end, x_init, x_end-1, z_init, z_end-1))
		return partitions

	if min_wrange > 1 and min_drange < 2:
		x_split = x_init + partition_min * RNG.randint(1, min_wrange-1)
		quadtreeSpacePartitioning(y_init, y_end, x_init, x_split, z_init, z_end, partitions, stop_chance)
		quadtreeSpacePartitioning(y_init, y_end, x_split, x_end, z_init, z_end, partitions, stop_chance)
	elif min_drange > 1 and min_wrange < 2:
		z_split = z_init + partition_min * RNG.randint(1, min_drange-1)
		quadtreeSpacePartitioning(y_init, y_end, x_init, x_end, z_init, z_split, partitions, stop_chance)
		quadtreeSpacePartitioning(y_init, y_end, x_init, x_end, z_split, z_end, partitions, stop_chance)
	else:
		x_split = x_init + partition_min * RNG.randint(1, min_wrange-1)
		z_split = z_init + partition_min * RNG.randint(1, min_drange-1)
		quadtreeSpacePartitioning(y_init, y_end, x_init, x_split, z_init, z_split, partitions, stop_chance)
		quadtreeSpacePartitioning(y_init, y_end, x_split, x_end, z_init, z_split, partitions, stop_chance)
		quadtreeSpacePartitioning(y_init, y_end, x_init, x_split, z_split, z_end, partitions, stop_chance)
		quadtreeSpacePartitioning(y_init, y_end, x_split, x_end, z_split, z_end, partitions, stop_chance)

	return partitions
