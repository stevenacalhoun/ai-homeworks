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

# My include
from random import shuffle

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
  nodes = []
  edges = []
  polys = []
  ### YOUR CODE GOES BELOW HERE ###
  test()
  return
  # Convert world information to my own classes
  worldPoints = []
  for point in world.getPoints():
    worldPoints.append(Point(point[0], point[1]))
  worldLines = []
  for line in world.getLinesWithoutBorders():
    worldLines.append(Line(Point(line[0][0], line[0][1]), Point(line[1][0], line[1][1])))
  worldObstacles = []
  for obstacle in world.getObstacles():
    obstacleLines = []
    for line in obstacle.lines:
      obstacleLines.append(Line(Point(line[0][0],line[0][1]),Point(line[1][0],line[1][1])))
    worldObstacles.append(Polygon(lines=obstacleLines))

  polys = createNavMesh(worldPoints, worldLines, worldObstacles)
  print str(len(polys)) + " Polys"
  nodes = createPathNodes(polys, worldLines)
  print str(len(nodes)) + " Nodes"
  edges = createPathLines(nodes, worldPoints, worldLines)
  print str(len(edges)) + " Edges"

  polys = polysToPointTuples(polys)
  nodes = pointsToTuples(nodes)
  edges = linesToTuples(edges)

  for node in nodes:
    drawCross(world.debug, node, color=(0,0,255))

  ### YOUR CODE GOES ABOVE HERE ###
  return nodes, edges, polys

################################################################################################
# Nav mesh creation
################################################################################################
# Create navmesh
def createNavMesh(worldPoints, worldLines, worldObstacles):
  # Create navmesh only out of triangles
  polys = createTriangleMesh(worldPoints, worldLines, worldObstacles)

  # Combine triangles to higher order polygons
  # polys = mergePolys(polys)

  return polys

# Create triangle mesh
def createTriangleMesh(worldPoints, worldLines, worldObstacles):
  completedPoints = []
  tris = []

  # Randomize point selection
  startingPoints = worldPoints
  shuffle(startingPoints)

  # Continue until all points covered
  for point in startingPoints:
    # Create triangles around this point
    createTrianglesFromPoint(worldPoints, worldLines, point, tris, worldObstacles)

  return tris

def createTrianglesFromPoint(worldPoints, worldLines, currentPoint, currentTris, worldObstacles):
  coveredSuccessors = []
  successors = getAllSuccessors(currentPoint, worldPoints, worldLines, worldObstacles)

  for successor1 in successors:
    # Start with an uncovered successor
    if successor1 not in coveredSuccessors:
      # Find a suitable second successor
      for successor2 in successors:
        if isSuccessor(successor1, successor2, worldLines, worldObstacles):
          testTri = Polygon(points=[currentPoint, successor1, successor2])

          # Make sure our test tri is unobstructed
          if not testTri.overlapsAnyPoly(currentTris):
            coveredSuccessors.append(successor1)
            coveredSuccessors.append(successor2)
            currentTris.append(testTri)

# Get all successors of a point
def getAllSuccessors(startPoint, worldPoints, worldLines, worldObstacles):
  successors = []
  for point in worldPoints:
    if isSuccessor(startPoint, point, worldLines, worldObstacles):
      successors.append(point)

  return successors

# Check if two lines are successors
def isSuccessor(point1, point2, worldLines, worldObstacles):
  for obstacle in worldObstacles:
    line = Line(point1,point2)
    if pointInsidePolygonLines(line.midpoint(), obstacle.toLineTuple()):
      return False

  # Lines along obstacleLines are okay
  if Line(point1,point2) in worldLines:
    return True
  if Line(point2,point1) in worldLines:
    return True

  # Lines through free space are okay
  if (rayTraceWorldNoEndPoints(point1, point2, worldLines) == None and point1 != point2):
    return True

  return False

def mergePolys(polys):
  mergeCount = 0
  for poly1 in polys:
    for poly2 in polys:
      combinedPoly = poly1.combinePoly(poly2)
      if combinedPoly != None:
        print
        print combinedPoly
        print combinedPoly.order
        polys = removePoly(poly1, polys)
        polys = removePoly(poly2, polys)
        polys.append(combinedPoly)
        mergeCount+=1

  print str(mergeCount) + " merges"
  return polys

################################################################################################
# Path node creation
################################################################################################
# Create path nodes from navmesh polys
def createPathNodes(polys,worldLines):
  nodes = []

  # For every shared line between polys, add a path node at the midpoint
  for poly1 in polys:
    for line in poly1.lines:
      if line not in worldLines:
        if line.midpoint() not in nodes:
          nodes.append(line.midpoint())

  return nodes

################################################################################################
# Path line creation
################################################################################################
# Create lines between pathnodes
def createPathLines(pathnodes, worldPoints, worldLines):
  lines = []
  coveredNodes = []

  # Check each node
  while len(coveredNodes) <= len(coveredNodes):
    print str(len(coveredNodes)) + "/" + str(len(pathnodes))
    for parentNode in pathnodes:
      visibleNodes = getAllUnobstructedLines(parentNode, pathnodes, worldPoints, worldLines)
      bestPathNode = findClosestUnobstructed(parentNode, visibleNodes,worldLines)
      if bestPathNode:
        newLine = Line(parentNode, bestPathNode)
        if newLine not in lines:
          lines.append(newLine)
          coveredNodes.append(parentNode)
          coveredNodes.append(bestPathNode)

  return lines

# Get all visible nodes
def getAllUnobstructedLines(parentNode, pathnodes, worldPoints, worldLines):
  visibleNodes = []

  # Check each node for each node
  for childNode in pathnodes:
    # Skip itself
    if parentNode != childNode:
      # Add line if unobstructed
      if lineUnobstructed(Line(parentNode, childNode), worldPoints, worldLines):
        visibleNodes.append(childNode)

  return visibleNodes

# Check if line is unobstructed
def lineUnobstructed(line, worldPoints, worldLines):
  # Ensure the line between the tow points doesn't intersect any object lines
  if rayTraceWorldNoEndPoints(line.p1, line.p2, worldLines) != None:
    return False

  # Make sure the agent won't clip any obstacle points along a line
  for point in worldPoints:
    ## This distance can be modified
    if minimumDistance([line.p1,line.p2], point) < 35.0:
      return False

  return True

################################################################################################
# Custom Point class instead of tuples
################################################################################################
class Point():
  def __init__(self, x, y):
    self.x = x
    self.y = y

    # Used for sorting in a clockwise manner
    self.center = None

  def __eq__(self, otherPoint):
    if otherPoint == None:
      return False
    if self.x == otherPoint.x and self.y == otherPoint.y:
      return True
    return False

  def __ne__(self, otherPoint):
    return not self.__eq__(otherPoint)

  def __lt__(self, other):
    if self.center == None:
      return False

    if self.x - self.center.x >= 0 and other.x - self.center.x < 0:
      return True
    if self.x - self.center.x < 0 and other.x - self.center.x >= 0:
        return False
    if self.x - self.center.x == 0 and other.x - self.center.x == 0:
      if self.y - self.center.y >= 0 or other.y - self.center.y >= 0:
        return self.y > other.y
      return other.y > self.y

    det = (self.x - self.center.x) * (other.y - self.center.y) - (other.x - self.center.x) * (self.y - self.center.y);
    if det < 0:
      return True
    if det > 0:
      return False

    d1 = (self.x - self.center.x) * (self.x - self.center.x) + (self.y - self.center.y) * (self.y - self.center.y)
    d2 = (other.x - self.center.x) * (other.x - self.center.x) + (other.y - self.center.y) * (other.y - self.center.y)
    return d1 > d2

  def __gt__(self, other):
    return not self.__lt__(other) and not self.__eq__(other)

  def __lq__(self, other):
    return self.__lt__(other) or self.__eq__(other)

  def __gq__(self, other):
    return self.__gt__(other) or self.__eq__(other)

  def __str__(self):
    return str(self.x)+","+str(self.y)

  def __repr__(self):
    return str(self)

  def __getitem__(self, key):
    if key == 0:
      return self.x
    if key == 1:
      return self.y

  def __add__(self, other):
    x = self.x + other.x
    y = self.y + other.y
    return Point(x,y)

  def __sub__(self, other):
    x = self.x - other.x
    y = self.y - other.y
    return Point(x,y)

  def __div__(self, other):
    if type(other) == int:
      x = self.x/other
      y = self.y/other
    if type(other) == Point:
      x = self.x/other.x
      y = self.y/other.y

    return Point(x,y)

  def toTuple(self):
    return (self.x,self.y)


################################################################################################
# Custom Line class for the same reasons
################################################################################################
class Line():
  def __init__(self, p1, p2):
    self.p1 = p1
    self.p2 = p2

  def __eq__(self, otherLine):
    if otherLine == None:
      return False
    if self.p1 == otherLine.p1 and self.p2 == otherLine.p2:
      return True
    if self.p2 == otherLine.p1 and self.p1 == otherLine.p2:
      return True
    return False

  def __ne__(self, otherLine):
    return not self.__eq__(otherLine)

  def __str__(self):
    return str(self.p1) + "<->" + str(self.p2)

  def __repr__(self):
    return str(self)

  def __getitem__(self, key):
    if key == 0:
      return self.p1
    if key == 1:
      return self.p2

  def midpoint(self):
    return Point((self.p1.x+self.p2.x)/2, (self.p1.y+self.p2.y)/2)

  def toTuple(self):
    return (self.p1.toTuple(),self.p2.toTuple())

  def intersects(self, otherLine):
    if rayTraceNoEndpoints(self.p1, self.p2, otherLine) and self != otherLine:
      return True
    return False

  def intersectsAny(self, worldLines):
    for line in worldLines:
      if self.intersects(line):
        return True
    return False

################################################################################################
# Custom Polygon class instead of...you already know by now
################################################################################################
class Polygon():
  def __init__(self, points=None, lines=None):
    self.points = []
    self.lines = []

    self.center = Point(0,0)

    if points != None:
      # Calculate center
      for point in points:
        self.center += point
      self.center = self.center/len(points)

      # Clockwisify the points
      self.points = sortPointsClockwise(points,self.center)

      # Convert to lines
      self._generateLines()

    if lines != None:
      self.lines = lines

      # Convert to points
      self._generatePoints()

    self.order = len(self.lines)

  def __eq__(self, otherPoly):
    if otherPoly == None:
      return False

    # Different number of lines
    if len(self.lines) != len(otherPoly.lines):
      return False

    for line in self.lines:
      if line not in otherPoly.lines:
        return False

    return True

  def __ne__(self, otherPoly):
    result = self.__eq__(otherPoly)
    return not result

  def __str__(self):
    returnStr = ""
    for line in self.lines:
      returnStr += str(line) + " "
    return returnStr

  def __repr__(self):
    return str(self)

  # Generate points based on lines
  def _generatePoints(self):
    # Add in all unique points
    points = []
    for line in self.lines:
      if line.p1 not in points:
        points.append(line.p1)
      if line.p2 not in points:
        points.append(line.p2)

    # Calculate center
    for point in points:
      self.center += point
    self.center = self.center/len(points)

    # Clockwisify points
    self.points = sortPointsClockwise(points,self.center)

  # Generate lines based on points
  def _generateLines(self):
    last = None
    for p in self.points:
      if last != None:
        self.lines.append(Line(last, p))
      last = p
    self.lines.append(Line(self.points[len(self.points)-1], self.points[0]))

  # Convert poly to list of point tuples
  def toPointTuple(self):
    points = []
    for point in self.points:
      points.append(point.toTuple())
    return points

  # Convert poly to list of line tuples
  def toLineTuple(self):
    lines = []
    for line in self.lines:
      lines.append(line.toTuple())
    return lines

  def pointInside(self, point):
    return pointInsidePolygonLines(point, self.lines) and not point in self.points and not pointOnPolygon(point,self.toPointTuple())

  # Check if line intersect poly
  def lineObstructs(self, testLine):
    # Line crosses inside
    if self.pointInside(testLine.p1) and self.pointInside(testLine.p2):
      return True

    # Line intersects
    if testLine.intersectsAny(self.lines):
      return True

    return False

  # Check if polygon overlaps
  def overlapsPoly(self, poly):
    for line in poly.lines:
      if self.lineObstructs(line):
        return True
    return False

  def overlapsAnyPoly(self, polys):
    for poly in polys:
      if self.overlapsPoly(poly):
        return True
    return False

  def combinePoly(self, otherPoly):
    # Check if polys are adjacent
    adjPoints = polygonsAdjacent(self.points, otherPoly.points)
    if adjPoints:
      # Combine two polys lines
      combinedPolyLines = []
      combinedPolyLines.extend(self.lines)
      combinedPolyLines.extend(otherPoly.lines)

      commonLine = Line(adjPoints[0],adjPoints[1])
      if commonLine in combinedPolyLines:
        combinedPolyLines = filter(lambda a: a != commonLine, combinedPolyLines)

      # New poly must be convex
      combinedPoly = Polygon(lines=combinedPolyLines)
      if combinedPoly.isConvex():
        return combinedPoly

      else:
        return None

    else:
      return None

  def isConvex(self):
    return isConvex(self.points)

# Point Lists
def pointsToTuples(points):
  tuples = []
  for point in points:
    tuples.append(point.toTuple())
  return tuples

def sortPointsClockwise(points, center):
  for point in points:
    point.center = center
  return sorted(points)

# Line Lists
def linesToTuples(lines):
  tuples = []
  for line in lines:
    tuples.append(line.toTuple())
  return tuples

# Poly Lists
def polysToPointTuples(polys):
  tuples = []
  for poly in polys:
    tuples.append(poly.toPointTuple())
  return tuples

def polysToLineTuples(polys):
  tuples = []
  for poly in polys:
    tuples.append(poly.toLineTuple())
  return tuples

def removePoly(deletedPoly, polys):
  polys = filter(lambda a: a != deletedPoly, polys)
  return polys

def test():
  p1 = Point(1,1)
  p12 = Point(1,1)
  p2 = Point(2,2)
  p3 = Point(3,3)
  p4 = Point(4,4)
  points = [p1,p2,p3]
  assert (p1 in points) == True
  assert (p12 in points) == True
  assert (p3 in points) == True
  assert (p4 in points) == False

  l1 = Line(p1,p2)
  l12 = Line(p2,p1)
  l2 = Line(p1,p3)
  l3 = Line(p3,p4)
  lines = [l1,l2]
  assert (l1 in lines) == True
  assert (l12 in lines) == True
  assert (l2 in lines) == True
  assert (l3 in lines) == False

  p1 = Point(10,10)
  p2 = Point(0,10)
  p3 = Point(0,0)
  p4 = Point(10,0)
  l1 = Line(p1,p2)
  l2 = Line(p2,p3)
  l3 = Line(p3,p4)
  l4 = Line(p4,p1)
  poly1 = Polygon(points=[p1,p4,p3,p2])
  poly2 = Polygon(lines=[l4,l2,l3,l1])
  assert (poly1.points == poly2.points) == True

  tri1 = Polygon(points=[p3,p4,p2])
  tri2 = Polygon(points=[p1,p4,p2])
  combinedPoly = tri1.combinePoly(tri2)
  assert (combinedPoly.points == poly1.points) == True
