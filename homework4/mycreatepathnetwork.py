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

# My includes
from random import randint
import math

# My constant for agent width
AGENT_WIDTH = 25.0

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
  nodes = []
  edges = []
  polys = []
  ### YOUR CODE GOES BELOW HERE ###

  # Convert objects
  worldPoints, worldLines, worldObstacles = convertWorldComponenets(world)

  # Create network
  nodeObjects, edgeObjects, polyObjects = createPathNetwork(worldPoints, worldLines, worldObstacles)

  # Convert my classes to expected output form
  polys = polysToPointTuples(polyObjects)
  nodes = pointsToTuples(nodeObjects)
  edges = linesToTuples(edgeObjects)

  ### NOT NEEDED
  # # Tests for my classes
  # classTests()
  #
  # # Check results
  # results(nodeObjects, edgeObjects, polyObjects, worldPoints, worldLines, worldObstacles, world)
  #
  # drawPathNetwork(nodeObjects, edgeObjects, polyObjects, world)
  ### NOT NEEDED

  ### YOUR CODE GOES ABOVE HERE ###
  return nodes, edges, polys

# Convert world information to my own classes
def convertWorldComponenets(world):
  # Convert world points obstacles to Points
  worldPoints = []
  for point in world.getPoints():
    worldPoints.append(Point(point[0], point[1]))

  # Convert world lines obstacles to Lines
  worldLines = []
  for line in world.getLines():
    worldLines.append(Line(Point(line[0][0], line[0][1]), Point(line[1][0], line[1][1])))

  # Convert world obstacles to Polygons
  worldObstacles = []
  for obstacle in world.getObstacles():
    obstacleLines = []
    for line in obstacle.lines:
      obstacleLines.append(Line(Point(line[0][0],line[0][1]),Point(line[1][0],line[1][1])))
    worldObstacles.append(Polygon(lines=obstacleLines))

  return worldPoints, worldLines, worldObstacles

# Create path network
def createPathNetwork(worldPoints, worldLines, worldObstacles):
  # Nav mesh
  print "Creating Nav Mesh"
  polys = createNavMesh(worldPoints, worldLines, worldObstacles)
  print str(len(polys)) + " Polys"
  print

  # Path nodes
  print "Creating Path Nodes"
  nodes = createPathNodes(polys, worldPoints, worldLines)
  print str(len(nodes)) + " Nodes"
  print

  # Path edges
  print "Creating Path Edges"
  edges = createPathLines(nodes, polys, worldPoints, worldLines)
  print str(len(edges)) + " Edges"
  print

  # Cleanup path network
  edgesPoints = linesToPoints(edges)
  for node in nodes:
    goodNode = True
    if node not in edgesPoints:
      nodes.remove(node)

  return nodes, edges, polys

################################################################################################
# Nav mesh creation
################################################################################################
# Create navmesh
def createNavMesh(worldPoints, worldLines, worldObstacles):
  # Create navmesh only out of triangles
  polys = createTriangleMesh(worldPoints, worldLines, worldObstacles)

  # Combine triangles to higher order polygons
  polys = mergePolys(polys)

  return polys

# Create triangle mesh
def createTriangleMesh(worldPoints, worldLines, worldObstacles):
  completedPoints = []
  tris = []

  # Continue until all points covered
  for point in worldPoints:
    # Create triangles around this point
    createTrianglesFromPoint(point, tris, worldPoints, worldLines, worldObstacles)

  return tris

def createTrianglesFromPoint(point, tris, worldPoints, worldLines, worldObstacles):
  successors = point.getAllSuccessors(worldPoints, worldLines, worldObstacles)

  for i,successor1 in enumerate(successors):
    # Find a suitable second successor
    for successor2 in successors[i:]:
      if successor1.isSuccessor(successor2, worldLines, worldObstacles):
        testTri = Polygon(points=[point, successor1, successor2])

        # Make sure our test tri is unobstructed and new
        if not testTri.overlapsAnyPoly(tris) and not testTri.overlapsAnyPoly(worldObstacles) and testTri not in tris and testTri not in worldObstacles:
          tris.append(testTri)

def mergePolys(polys):
  mergeCount = 0
  # Try to merge every poly with every other poly
  for poly1 in polys:
    for poly2 in polys:
      combinedPoly = poly1.combinePoly(poly2)
      if combinedPoly != None:
        ### This shouldn't be the way, every time I merge, I should restart these loops
        if poly1 in polys:
          polys.remove(poly1)
        if poly2 in polys:
          polys.remove(poly2)
        polys.append(combinedPoly)
        mergeCount+=1

  return polys

################################################################################################
# Path node creation
################################################################################################
# Create path nodes from navmesh polys
def createPathNodes(polys, worldPoints, worldLines):
  nodes = []

  # Add a node at the midpoint of every mesh line through free space
  for poly in polys:
    for line in poly.lines:
      if line not in worldLines and line.agentCanFollow(worldPoints, worldLines):
        if line.midpoint() not in nodes:
          nodes.append(line.midpoint())

  return nodes

################################################################################################
# Path line creation
################################################################################################
# Create lines between pathnodes
def createPathLines(pathnodes, polys, worldPoints, worldLines):
  lines = []

  # Construct hull inclusions dictionary
  hullInclusions = {}
  for node in pathnodes:
    includedHulls = []
    # Find all the hulls this node is part of
    for poly in polys:
      if poly.hullIncludesPoint(node):
        includedHulls.append(poly)

    # All the hulls for this point, should never be more than 2
    hullInclusions[node] = includedHulls

  # Find all the node pairs that share a hull
  for parentNode in pathnodes:
    for testNode in pathnodes:
      for hull in hullInclusions[parentNode]:
        if hull in hullInclusions[testNode]:
          # New line, actually a line, agent can get by without collision on line
          testLine = Line(parentNode,testNode)
          if testLine not in lines and parentNode != testNode and testLine.agentCanFollow(worldPoints, worldLines):
            lines.append(testLine)

  return lines

################################################################################################
# Custom Point class instead of tuples
################################################################################################
class Point(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y

    # Used for sorting in a clockwise manner
    self.center = None;

  # Overloaded operators
  def __eq__(self, otherPoint):
    if type(otherPoint) is not Point:
      return False
    if self.x == otherPoint.x and self.y == otherPoint.y:
      return True
    return False

  def __ne__(self, otherPoint):
    return not self.__eq__(otherPoint)

  ## CITATION
  # This code is taken from a stack overflow post. I implemented a point compare
  # function so that I could then sort a list of points around a center.
  # URL: http://stackoverflow.com/questions/6989100/sort-points-in-clockwise-order
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
  ## END CITATION

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
    return None

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

  # Point as an x,y tuple
  def toTuple(self):
    return (self.x,self.y)

  # Check if point is a successor
  def isSuccessor(self, otherPoint, worldLines, worldObstacles):
    # Lines along obstacleLines are okay
    if Line(self,otherPoint) in worldLines:
      return True

    # Lines that stretch obstaclePoint to obstaclePoint but not along an obstacle edge, this would result a false True using rayTraceWorldNoEndPoints
    for obstacle in worldObstacles:
      line = Line(self,otherPoint)
      if pointInsidePolygonLines(line.midpoint(), obstacle.toLineTuple()):
        return False

    # Lines through free space are okay
    if (rayTraceWorldNoEndPoints(self, otherPoint, worldLines) == None and self != otherPoint):
      return True

    return False

  # Get all successors
  def getAllSuccessors(self, worldPoints, worldLines, worldObstacles):
    successors = []
    for worldPoint in worldPoints:
      if self.isSuccessor(worldPoint, worldLines, worldObstacles):
        successors.append(worldPoint)

    return successors

################################################################################################
# Custom Line class for the same reasons
################################################################################################
class Line(object):
  def __init__(self, p1, p2):
    self.p1 = p1
    self.p2 = p2
    self.length = math.sqrt(math.pow(p2.x - p1.x,2) + math.pow(p2.y - p1.y,2))

  # Overloaded operators
  def __eq__(self, otherLine):
    if type(otherLine) != Line:
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
    return None

  # Return tuple of point tuples
  def toTuple(self):
    return (self.p1.toTuple(),self.p2.toTuple())

  def center(self, center):
    line = Line(self.p1-center, self.p2-center)
    return line

  # Midpoint of line
  def midpoint(self):
    return Point((self.p1.x+self.p2.x)/2.0, (self.p1.y+self.p2.y)/2.0)

  # Line intersects line
  def intersects(self, otherLine):
    if rayTraceNoEndpoints(self.p1, self.p2, otherLine) and self != otherLine:
      return True
    return False

  # Line intersects any line in list
  def intersectsAny(self, otherLines):
    for otherLine in otherLines:
      if self.intersects(otherLine):
        return True
    return False

  # Check if agent can follow line
  def agentCanFollow(self, worldPoints, worldLines):
    # Make sure the agent won't clip any obstacle points along a line
    for point in worldPoints:
      if minimumDistance([self.p1, self.p2], point) < AGENT_WIDTH and self not in worldLines and point != self.p1 and point != self.p2:
        return False

    return True

################################################################################################
# Custom Polygon class instead of...you already know by now
################################################################################################
class Polygon(object):
  def __init__(self, points=None, lines=None, area=None):
    self.points = []
    self.lines = []
    self.centroid = Point(0,0)
    self.areaVal = None

    ## Init with points
    if points != None:
      self.points = points
      self._generateLines()

    ## Init with lines
    if lines != None:
      self.lines = lines
      self._generatePoints()

    # Clockwisify points
    self._calculateCentroid()
    self.points = sortPointsClockwise(self.points,self.centroid)
    self.order = len(self.lines)

  # Overloaded operators
  def __eq__(self, otherPoly):
    if type(otherPoly) != Polygon:
      return False
    if len(self.lines) != len(otherPoly.lines):
      return False
    for line in self.lines:
      if line not in otherPoly.lines:
        return False
    return True

  def __ne__(self, otherPoly):
    return not self.__eq__(otherPoly)

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
    self.points = []
    for line in self.lines:
      if line.p1 not in self.points:
        self.points.append(line.p1)
      if line.p2 not in self.points:
        self.points.append(line.p2)

  # Generate lines based on points
  def _generateLines(self):
    last = None
    for p in self.points:
      if last != None:
        self.lines.append(Line(last, p))
      last = p
    self.lines.append(Line(self.points[len(self.points)-1], self.points[0]))

  # Calculate centroid
  def _calculateCentroid(self):
    for point in self.points:
      self.centroid += point
    self.centroid = self.centroid/len(self.points)

  def area(self):
    # See if it's already been calculated
    if self.areaVal != None:
      return self.area

    self.areaVal = 0
    # Triangle
    if self.order == 3:
      b = Line(self.points[1],self.points[0]).center(self.points[1])
      a = Line(self.points[1],self.points[2]).center(self.points[1])
      self.areaVal += 0.5*a.length*b.length*math.sin(angle(a.p2.toTuple(),b.p2.toTuple()))

    # Higher order poly
    else:
      for i,point in enumerate(self.points):
        if i == len(self.points)-1:
          tri = Polygon(points=[self.centroid, self.points[i], self.points[0]])
        else:
          tri = Polygon(points=[self.centroid, self.points[i], self.points[i+1]])
        self.areaVal += tri.area()

    return self.areaVal

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

  # Point part of hull
  def hullIncludesPoint(self, point):
    return pointInsidePolygonLines(point, self.lines) or point in self.points or pointOnPolygon(point,self.toPointTuple())

  # Point inside poly
  def pointInside(self, point):
    return pointInsidePolygonLines(point, self.lines) and not point in self.points and not pointOnPolygon(point,self.toPointTuple())

  # Check if line intersect poly
  def lineObstructs(self, testLine):
    # Line crosses inside
    if self.pointInside(testLine.p1) or self.pointInside(testLine.p2):
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

  # Overlaps any poly in a list
  def overlapsAnyPoly(self, polys):
    for poly in polys:
      if self.overlapsPoly(poly):
        return True
    return False

  # Combine two polys, return combined poly, None otherwise
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

    return None

  # Polygon is convex
  def isConvex(self):
    return isConvex(self.points)

################################################################################################
# Lists of my objects helpers
################################################################################################
##### Point Lists
# Points to list of tuples
def pointsToTuples(points):
  tuples = []
  for point in points:
    tuples.append(point.toTuple())
  return tuples

# Sort list of points to be clockwise around a center
def sortPointsClockwise(points, center):
  for point in points:
    point.center = center
  return sorted(points)

##### Line Lists
# Lines to a list of point tuples pairs
def linesToTuples(lines):
  tuples = []
  for line in lines:
    tuples.append(line.toTuple())
  return tuples

# Lines to a list of unique points
def linesToPoints(lines):
  points = []
  for line in lines:
    if line.p1 not in points:
      points.append(line.p1)
    if line.p2 not in points:
      points.append(line.p2)
  return points

##### Poly Lists
# Polys to a list of point tuples pairs
def polysToPointTuples(polys):
  tuples = []
  for poly in polys:
    tuples.append(poly.toPointTuple())
  return tuples

# Polys to a list of line tuples
def polysToLineTuples(polys):
  tuples = []
  for poly in polys:
    tuples.append(poly.toLineTuple())
  return tuples

################################################################################################
# Draw functions
################################################################################################
# Draw network my way
def drawPathNetwork(nodes, edges, polys, world):
  # # Draw nav mesh area (no way to get it transparent)
  # for i,poly in enumerate(polys):
  #   pygame.draw.polygon(world.debug, randomColor(), poly.toPointTuple())

  # Lines on edges
  for edge in edges:
    pygame.draw.line(world.debug, (0,0,255), edge.p1.toTuple(), edge.p2.toTuple(), 1)

  # Crosses on nodes
  for node in nodes:
    drawCross(world.debug, node.toTuple(), color=(0,0,0), size=3, width=2)

def randomColor():
  return (randint(50,255),randint(50,255),randint(50,255))

################################################################################################
# Tests
################################################################################################
# Test end result
def results(nodes, edges, polys, worldPoints, worldLines, worldObstacles, world):
  print "########################"
  print "Results"
  print "########################"

  # Reachability results
  reachable = reachabilityResults()

  # Coverage results
  covered = coverageResults(polys, worldObstacles, world)

  # Mesh results
  optimized = meshOptimizationResults(polys)

  # Draw eveyrthing if something is wrong
  if reachable and covered and optimized:
    print "PASSED"
  else:
    print "FAILED"
    drawPathNetwork(nodes, edges, polys, world)

  return

# Reachability results
def reachabilityResults():
  print "Reachability results"
  print "Dunno how to test this"
  print

  result = True

  return result

# Coverage results
def coverageResults(polys, worldObstacles, world):
  print "Coverage results"

  for obstacle in worldObstacles:
    if not obstacle.isConvex():
      print "Can't check coverage, non convex shapes in world"
      print
      return True

  # Check that everything is covered
  navigableArea = world.dimensions[0]*world.dimensions[1]
  for obstacle in worldObstacles:
    navigableArea -= obstacle.area()

  meshArea = 0
  for poly in polys:
    meshArea += poly.area()

  # Coverage is good
  if closeToEqual(meshArea,navigableArea):
    result = True
    print "Everything is covered"

  # Coverage is off
  else:
    result = False

    print "World: " + str(navigableArea)
    print "Mesh: " + str(meshArea)
    if meshArea > navigableArea:
      print "Too much coverage"
    else:
      print "Too little coverage"

  print
  return result

# Mesh optimization reslts
def meshOptimizationResults(polys):
  print "Mesh Optimization Results"

  # Ensure highest order is greater than 3
  highestOrder = 0
  for poly in polys:
    if poly.order > highestOrder:
      highestOrder = poly.order

  if highestOrder > 3:
    print "Highest order good: " + str(highestOrder)
    result = True
  else:
    print "Highest order too low: " + str(highestOrder)
    result = False

  print
  return result

def closeToEqual(val1, val2, thresh=1.0):
  return val1 > (val2-thresh) and val1 < (val2+thresh)

# Testing classes
def classTests():
  print "########################"
  print "Class tests"
  print "########################"
  # p1 = Point(1,1)
  # p12 = Point(1,1)
  # p2 = Point(2,2)
  # p3 = Point(3,3)
  # p4 = Point(4,4)
  # points = [p1,p2,p3]
  # assert (p1 in points) == True
  # assert (p12 in points) == True
  # assert (p3 in points) == True
  # assert (p4 in points) == False
  #
  # l1 = Line(p1,p2)
  # l12 = Line(p2,p1)
  # l2 = Line(p1,p3)
  # l3 = Line(p3,p4)
  # lines = [l1,l2]
  # assert (l1 in lines) == True
  # assert (l12 in lines) == True
  # assert (l2 in lines) == True
  # assert (l3 in lines) == False
  #
  p1 = Point(20,10)
  p2 = Point(10,10)
  p3 = Point(10,0)
  p4 = Point(20,0)
  l1 = Line(p1,p2)
  l2 = Line(p2,p3)
  l3 = Line(p3,p4)
  l4 = Line(p4,p1)
  poly1 = Polygon(points=[p1,p4,p3,p2])
  poly2 = Polygon(lines=[l4,l2,l3,l1])
  assert (poly1.points == poly2.points) == True

  tri1 = Polygon(points=[p3,p4,p2])
  tri2 = Polygon(points=[p1,p4,p2])
  square = tri1.combinePoly(tri2)
  tri3 = Polygon(points=[p4,p1,Point(30,0)])
  hexShape = square.combinePoly(tri3)
  secondSquare = Polygon(points=[Point(0,0),Point(10,10),Point(10,0),Point(0,10)])
  weirdShape = hexShape.combinePoly(secondSquare)
  assert (square.points == poly1.points) == True
  assert (closeToEqual(weirdShape.area(), 250, thresh=0.0001))

  print "PASSED"
  print
