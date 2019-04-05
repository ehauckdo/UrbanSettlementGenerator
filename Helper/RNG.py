import random
import numpy as np

def getStateFromString(state):
    import hashlib
    return int(hashlib.md5(state).hexdigest()[:8], 16)

rng_dictionary = {}
rng_dictionary[getStateFromString("default")] = np.random.RandomState(10)

def randint(minimum, maximum, state="default"):
	if getStateFromString(state) not in rng_dictionary.keys():
		rng_dictionary[getStateFromString(state)]  = np.random.RandomState()

	if minimum == maximum:
		return minimum

	return rng_dictionary[getStateFromString(state)].randint(minimum, maximum)

def random(state="default"):
	if getStateFromString(state) not in rng_dictionary.keys():
		rng_dictionary[getStateFromString(state)]  = np.random.RandomState()

	return rng_dictionary[getStateFromString(state)].rand()

def choice(list_objects, how_many=1, state="default"):
	if getStateFromString(state) not in rng_dictionary.keys():
		rng_dictionary[getStateFromString(state)]  = np.random.RandomState()

	return rng_dictionary[getStateFromString(state)].choice(list_objects, how_many)

def setSeed(state, seed):
	rng_dictionary[getStateFromString(state)] = np.random.RandomState(seed)

def shuffle(list, state="default"):
	if getStateFromString(state) not in rng_dictionary.keys():
		rng_dictionary[getStateFromString(state)]  = np.random.RandomState()

	return rng_dictionary[getStateFromString(state)].shuffle(list)
