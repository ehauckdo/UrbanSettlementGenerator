#!/usr/bin/env python
# coding: utf-8

import numpy as np
import random

carpetID = 171

# Sub generators

def border(matrix, color, h, x_min, x_max, z_min, z_max):
    for i in range(x_min, x_max):
        matrix[h][i][z_min] = (carpetID, color)
        matrix[h][i][z_max-1] = (carpetID, color)
    for i in range(z_min, z_max):
        matrix[h][x_min][i] = (carpetID, color)
        matrix[h][x_max-1][i] = (carpetID, color)        
    
def full(matrix, color, h, x_min, x_max, z_min, z_max):
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            matrix[h][x][z] = (carpetID, color)
            
def checkers(matrix, color, h, x_min, x_max, z_min, z_max):
    count = 0
    for x in range(x_min, x_max):
        count = x % 2
        for z in range(z_min, z_max):
            matrix[h][x][z] = (carpetID, color[count])
            count = (count + 1) % 2

# Main generators

def full_and_border(matrix, h, x_min, x_max, z_min, z_max):
    c = np.random.choice(16, 2, replace = False)
    c = np.sort(c)
    full(matrix, c[0], h, x_min, x_max, z_min, z_max)
    border(matrix, c[1], h, x_min, x_max, z_min, z_max)    
    
def checkers_and_border(matrix, h, x_min, x_max, z_min, z_max):
    c = np.random.choice(16, 3, replace = False)
    c = np.sort(c)
    checkers(matrix, (c[0],c[1]), h, x_min, x_max, z_min, z_max)
    border(matrix, c[2], h, x_min, x_max, z_min, z_max)

def circles(matrix, h, x_min, x_max, z_min, z_max):
    # Feature, not bug
    c = np.random.choice(16, 2, replace = False)
    c = np.sort(c)
    count = 0
    xs, xe, zs, ze = x_min, x_max, z_min, z_max
    while xs <= xe and zs <= ze:
        border(matrix, c[count], h, xs, xe, zs, ze)
        count = (count + 1) % 2
        xs, xe, zs, ze = xs+1, xe-1, zs+1, ze-1

# Main function:

def generateCarpet(matrix, h, x_min, x_max, z_min, z_max):
    functions = [full_and_border, 
                 circles,
                 checkers_and_border]
    weights = [0.4, 0.4, 0.2]
    f = np.random.choice(functions, p = weights)
    f(matrix, h, x_min, x_max, z_min, z_max)

