
def generateCentralTable(world, y, x, z):
	world.setValue(y+1, x, z, (85,0))
	world.setValue(y+2, x, z, (72,0))
	world.setValue(y+1, x-1, z, (53, 1))
	world.setValue(y+1, x+1, z, (53, 0))

def generateBookshelf(world, y, x, z):
	world.setValue(y+1, x-1, z-1, (47,0))
	world.setValue(y+1, x-2, z-1, (47,0))
	world.setValue(y+2, x-1, z-1, (47,0))
	world.setValue(y+2, x-2, z-1, (47,0))

def generateCouch(world, y, x, z):
	world.setValue(y+1, x+4, z-1, (53, 0))
	world.setValue(y+1, x+3, z-1, (53, 2))
	world.setValue(y+1, x+2, z-1, (53, 1))

def generateChandelier(world, y, x, z):
	world.setValue(y-1, x, z, (85,0))
	world.setValue(y-2, x, z, (169,0))

def generateBed(world, y, x, z):
	world.setValue(y+1, x-1, z+1, (35,14))
	world.setValue(y+1, x-2, z+1, (35,14))