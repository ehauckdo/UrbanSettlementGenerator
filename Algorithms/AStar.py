import logging

class Node():

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

def aStar(p1, p2, pathMap, height_map):

	logging.info("(A*) Searching a path between {} and {}".format(p1, p2))

	start_node = Node(None, (p1[1], p1[2]))
	start_node.g = start_node.h = start_node.f = 0
	end_node = Node(None, (p2[1], p2[2]))
	end_node.g = end_node.h = end_node.f = 0

	# Initialize both open and closed list
	open_dict = {}
	closed_dict = {}

	# Add the start node
	open_dict[start_node.position] = start_node
	iterations = 0

	 # Loop until you find the end
	while len(open_dict.values()) > 0:

		# Get the current node
		current_node = sorted(open_dict.values(), key=lambda x: x.f)[0]
		
		# Pop current off open list, add to closed list
		open_dict.pop(current_node.position, None)
		closed_dict[current_node.position] = current_node

		# Found the goal
		if current_node.position == end_node.position:
			logging.info("(A*) Finished search, found a path between {} and {}, Total iterations; {}".format(p1, p2, iterations))
			path = []
			current = current_node
			while current is not None:
				path.append(current.position)
				current = current.parent
			return path[::-1] # Return reversed path

		children = []
		
		for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

			iterations +=1

			# Get node position
			node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
			#logging.info("Testing new position {}".format(node_position))

			# Make sure within range
			try:
				map = pathMap[node_position[0]][node_position[1]]
				#logging.info("Passed range test!")
			except IndexError:
				#out of range!
				continue

			# Create new node
			new_node = Node(current_node, node_position)

			direction = getDirectionFromParent(current_node, new_node)
			#logging.info("direction from parent {} = {}".format(current_node.position, direction))

			# Make sure walkable terrain
			if pathMap[current_node.position[0]][current_node.position[1]][direction] == -1 and node_position != end_node.position:
				#logging.info("Failed pathMap test!")
				continue
			
			# Append
			children.append(new_node)

		# Loop through children
		for child in children:
			#logging.info("Checking child {}".format(child.position))
			direction = getDirectionFromParent(current_node, child)
			#print("direction from parent ", current_node.position, " = ", direction)
			g = pathMap[current_node.position[0]][current_node.position[1]][direction]
			#logging.info("Pathmap value (g): {}".format(g))	

			# Skip this child if already in the closed list
			try:
				closed_child = closed_dict[child.position]
				continue
			except KeyError:
				pass

			# Create the f, g, and h values
			child.g = current_node.g + (1 + g**2)
			child.h = getManhattanDistance(child.position, end_node.position)
			child.f = child.g + child.h

			
			# Skip this child if already in the open list
			try:
				open_child = open_dict[child.position]
				continue
			except KeyError:
				pass

			open_dict[child.position] = child

	logging.info("(A*) Finished search, could not found a path between {} and {}, Total iterations; {}".format(p1, p2, iterations))

def getManhattanDistance(p1,p2):
	distance = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
	return distance

def getDirectionFromParent(parent, child):
	x = parent.position[0] - child.position[0]
	if x > 0:
		return "left"
	if x < 0:
		return "right"
	z = parent.position[1] - child.position[1]
	if z > 0:
		return "down"
	if z < 0:
		return "up"