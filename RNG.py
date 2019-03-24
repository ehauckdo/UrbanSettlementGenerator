import random
import numpy as np

def getStateFromString(state):
    import hashlib
    return int(hashlib.md5(state).hexdigest()[:8], 16)

rng_dictionary = {}
rng_dictionary[getStateFromString("default")] = np.random.RandomState()

def randint(min, max, state="default"):
	if getStateFromString(state) not in rng_dictionary.keys():
		rng_dictionary[getStateFromString(state)]  = np.random.RandomState()

	return rng_dictionary[getStateFromString(state)].randint(min, max)

def rand(state="default"):
	if getStateFromString(state) not in rng_dictionary.keys():
		rng_dictionary[getStateFromString(state)]  = np.random.RandomState()

	return rng_dictionary[getStateFromString(state)].rand()

def setSeed(state, seed):
	rng_dictionary[getStateFromString(state)] = np.random.RandomState(seed)

