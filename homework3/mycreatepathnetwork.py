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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
  nodes = []
  edges = []
  polys = []
  ### YOUR CODE GOES BELOW HERE ###

  polys = createNavMesh(world.getPoints(), world.getLinesWithoutBorders())
  nodes = createPathNodes(polys)
  edges = createPathLines(nodes, world.getPoints(), world.getLinesWithoutBorders())

  ### YOUR CODE GOES ABOVE HERE ###
  return nodes, edges, polys

# Create navmesh
def createNavMesh(obstaclePoints, obstacleLines):
  # Create navmesh only out of triangles
  tris = createTriangleMesh(obstaclePoints, obstacleLines)

  # Combine triangles to higher order polygons
  polys = combineTriangles(tris)

  return polys

# Create triangle mesh
def createTriangleMesh(obstaclePoints, obstacleLines):
  coveredPoints = []
  tris = []

  # Continue until all points covered
  while len(obstaclePoints) != len(coveredPoints):
    # Pick a new starting point
    currentPoint = None
    for point in obstaclePoints:
      if point not in coveredPoints:
        currentPoint = point
        break

    # Get two successor points
    firstSuccessor = findSuccessor(obstaclePoints, obstacleLines, currentPoint)
    secondSuccessor = findSuccessor(obstaclePoints, obstacleLines, currentPoint, firstSuccessor)

    # Mark points as covered
    if currentPoint not in coveredPoints:
      coveredPoints.append(currentPoint)
    if firstSuccessor not in coveredPoints:
      coveredPoints.append(firstSuccessor)
    if secondSuccessor not in coveredPoints:
      coveredPoints.append(secondSuccessor)

    # Add tri
    tris.append([currentPoint, firstSuccessor, secondSuccessor])

  return tris

# Find a suitable successor to 1 or 2 points
def findSuccessor(obstaclePoints, obstacleLines, point1, point2=None):
  if point2 == None:
    for point in obstaclePoints:
      if rayTraceWorldNoEndPoints(point1, point, obstacleLines) == None and point != point1:
        return point
  else:
    for point in obstaclePoints:
      if (rayTraceWorldNoEndPoints(point1, point, obstacleLines) == None) and (rayTraceWorldNoEndPoints(point2, point, obstacleLines) == None) and point != point1 and point != point2:
        return point

  print "Returned nothing"

# Combine triangles to higher order convex polys
def combineTriangles(tris):
  return tris

# Create path nodes from navmesh polys
def createPathNodes(polys):
  nodes = []

  # For every shared line between polys, add a path node at the midpoint
  for poly1 in polys:
    for poly2 in polys:
      adjacentPoints = polygonsAdjacent(poly1, poly2)
      if adjacentPoints:
        nodes.append(getMidPoint(adjacentPoints[0], adjacentPoints[1]))

  return nodes

# Create lines between pathnodes
def createPathLines(pathnodes, obstaclePoints, obstacleLines):
  lines = []

  # Check each node
  for parentNode in pathnodes:
    # Check each node for each node
    for childNode in pathnodes:
      # Skip itself
      if parentNode != childNode:
        # Add line if unobstructed
        if lineUnobstructed(parentNode, childNode, obstaclePoints, obstacleLines):
          appendLineNoDuplicates([parentNode, childNode],lines)

  return lines

# Check if line is unobstructed
def lineUnobstructed(p1, p2, obstaclePoints, obstacleLines):
  # Ensure the line between the tow points doesn't intersect any object lines
  if rayTraceWorld(p1, p2, obstacleLines) != None:
    return False

  # Make sure the agent won't clip any obstacle points along a line
  for point in obstaclePoints:
    ## This distance can be modified
    if minimumDistance([p1,p2], point) < 35.0:
      return False

  return True

# Get midpoint of line
def getMidPoint(point1, point2):
  mid = [(point1[0]+point2[0])/2, (point1[1]+point2[1])/2]
  return mid
