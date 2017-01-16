'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates a grid as a 2D array of True/False values (True =  traversable). Also returns the dimensions of the grid as a (columns, rows) list.
def myCreateGrid(world, cellsize):
  ### YOUR CODE GOES BELOW HERE ###

  # Get dimensions
  numCols = int(round(SCREEN[0]/cellsize))
  numRows = int(round(SCREEN[1]/cellsize))
  dimensions = (numCols, numRows)

  # Create grid of all True
  grid = numpy.full((numCols, numRows), True, dtype=bool)

  # Check each space in the grid
  for colCount, col in enumerate(grid):
    for rowCount, row in enumerate(col):
      # Check if there is an obstacle in this space
      if containsObstacle(colCount, rowCount, cellsize, world):
        grid[colCount][rowCount] = False

  ### YOUR CODE GOES ABOVE HERE ###
  return grid, dimensions

def containsObstacle(col, row, cellsize, world):
  # Get corners of the space
  topLeft = (col*cellsize, row*cellsize)
  topRight = ((col+1)*cellsize, (row)*cellsize)
  botLeft = ((col)*cellsize, (row+1)*cellsize)
  botRight = ((col+1)*cellsize, (row+1)*cellsize)

  # Check if any of these corners are in any of the obstacles
  obstacles = world.getObstacles()
  for obstacle in obstacles:
    if obstacle.pointInside(topLeft) or obstacle.pointInside(topRight) or obstacle.pointInside(botLeft) or obstacle.pointInside(botRight):
      return True

  return False
