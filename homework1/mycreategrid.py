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
  dimensions = (int(round(world.dimensions[0]/cellsize)), int(round(world.dimensions[1]/cellsize)))

  # Create grid of all True
  grid = numpy.full((dimensions[0], dimensions[1]), True, dtype=bool)

  # Check each space in the grid
  for rowCount in xrange(dimensions[1]):
    for colCount in xrange(dimensions[0]):
      # Check if there is an obstacle in this space
      grid[colCount][rowCount] = cellObstacleFree(rowCount, colCount, cellsize, world)

  ### YOUR CODE GOES ABOVE HERE ###
  return grid, dimensions

# 1. If the lines that make up the four borders of the cell intersect any of the boundary or obstacle lines.
# 2. If the cell lies entirely within any of the obstacles.
def cellObstacleFree(row, col, cellsize, world):
  # Get corners of the cell
  topL = ((col+0)*cellsize, (row+0)*cellsize)
  topR = ((col+1)*cellsize, (row+0)*cellsize)
  botL = ((col+0)*cellsize, (row+1)*cellsize)
  botR = ((col+1)*cellsize, (row+1)*cellsize)

  # Lines of cell
  cellLines = [(topL, topR), (topR, botR), (botR, botL), (botL, topL)]

  # Check if any obstacle line intersects this cell's borders
  for line in world.getLinesWithoutBorders():
  # for line in world.getLines():
    for cellLine in cellLines:
      if calculateIntersectPoint(line[0], line[1], cellLine[0], cellLine[1]):
        return False

  # Check if any cell point lies with in an obstacle
  for obstacle in world.getObstacles():
    if obstacle.pointInside(topL) or obstacle.pointInside(topR) or obstacle.pointInside(botL) or obstacle.pointInside(botR):
      return False

  # Check if any obstacle point lies with cell
  for obstacle in world.getObstacles():
    for obstaclePoint in obstacle.getPoints():
      if pointInsidePolygonLines(obstaclePoint, cellLines):
        return False

  return True
