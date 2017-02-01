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
  test()

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

# Create navmesh
def createNavMesh(worldPoints, worldLines, worldObstacles):
  # Create navmesh only out of triangles
  polys = createTriangleMesh(worldPoints, worldLines, worldObstacles)

  # Combine triangles to higher order polygons
  keepGoing = True
  keepGoing = False
  while keepGoing:
    combinedPoly, poly1, poly2 = combinePolysOnce(polys)

    if combinedPoly != None:
      print "Combining"
      removePoly(poly1, polys)
      removePoly(poly2, polys)
      polys.append(combinedPoly)
    else:
      keepGoing = False

  return polys

# Create triangle mesh
def createTriangleMesh(worldPoints, worldLines, worldObstacles):
  completedPoints = []
  tris = []

  # Continue until all points covered
  for point in worldPoints:

    # Create triangles around this point
    createTrianglesFromPoint(worldPoints, worldLines, point, tris, worldObstacles)

  return tris

# Get all successors of a point
def getAllSuccessors(startPoint, worldPoints, worldLines, worldObstacles):
  successors = []
  for point in worldPoints:
    if isSuccessor(startPoint, point, worldLines, worldObstacles):
      successors.append(point)

  return successors

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
          if testTri.unobstructed(worldPoints, worldLines, currentTris):
            coveredSuccessors.append(successor1)
            coveredSuccessors.append(successor2)
            currentTris.append(testTri)

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

# Combine triangles to higher order convex polys
def combinePolysOnce(polys):
  for poly1 in polys:
    for poly2 in polys:
      combinedPoly = poly1.combinePoly(poly2)
      if combinedPoly != None:
        return combinedPoly, poly1, poly2
  return None, None, None

# Create path nodes from navmesh polys
def createPathNodes(polys,worldLines):
  nodes = []

  # For every shared line between polys, add a path node at the midpoint
  for poly1 in polys:
    for line in poly1.lines:
      if line not in worldLines:
        appendPointNoDuplicates(line.midpoint(), nodes)

  return nodes

# Create lines between pathnodes
def createPathLines(pathnodes, worldPoints, worldLines):
  lines = []

  # Check each node
  for parentNode in pathnodes:
    visibleNodes = getAllVisbileNodes(parentNode, pathnodes, worldPoints, worldLines)
    bestPathNode = findClosestUnobstructed(parentNode, visibleNodes,worldLines)
    if bestPathNode:
      newLine = Line(parentNode, bestPathNode)
      if newLine not in lines:
        lines.append(newLine)

  return lines

def getAllVisbileNodes(parentNode, pathnodes, worldPoints, worldLines):
  visibleNodes = []

  # Check each node for each node
  for childNode in pathnodes:
    # Skip itself
    if parentNode != childNode:
      # Add line if unobstructed
      if lineUnobstructed(parentNode, childNode, worldPoints, worldLines):
        visibleNodes.append(childNode)
  return visibleNodes

# Check if line is unobstructed
def lineUnobstructed(p1, p2, worldPoints, worldLines):
  # Ensure the line between the tow points doesn't intersect any object lines
  if rayTraceWorldNoEndPoints(p1, p2, worldLines) != None:
    return False

  # Make sure the agent won't clip any obstacle points along a line
  for point in worldPoints:
    ## This distance can be modified
    if minimumDistance([p1,p2], point) < 35.0:
      return False

  return True

def appendPointNoDuplicates(point, points):
  if point in points:
    return points
  else:
    return points.append(point)

def removePoly(deletedPoly, polys):
  polys.remove(deletedPoly)

class Point():
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __eq__(self, otherPoint):
    if otherPoint == None:
      return False
    if self.x == otherPoint.x and self.y == otherPoint.y:
      return True
    return False

  def __ne__(self, otherPoint):
    return not self.__eq__(otherPoint)

  def __str__(self):
    return "("+str(self.x)+","+str(self.y)+")"

  def __getitem__(self, key):
    if key == 0:
      return self.x
    if key == 1:
      return self.y

  def toTuple(self):
    return (self.x,self.y)

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

  def __getitem__(self, key):
    if key == 0:
      return self.p1
    if key == 1:
      return self.p2

  def midpoint(self):
    return Point((self.p1.x+self.p2.x)/2, (self.p1.y+self.p2.y)/2)

  def toTuple(self):
    return (self.p1.toTuple(),self.p2.toTuple())

class Polygon():
  def __init__(self, points=None, lines=None):
    self.points = []
    self.lines = []

    if points != None:
      # Add all points
      for point in points:
        if point not in self.points:
          self.points.append(point)

      # Conver to lines
      self.lines = createLineRepOfPolyPoints(self.points)

    if lines != None:
      # Add all lines
      for line in lines:
        if line not in self.lines:
          self.lines.append(line)

      # Convert to points
      self.points = createPointRepOfPolyLines(self.lines)

  def __eq__(self, otherPoly):
    if otherPoly == None:
      return False

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
      returnStr += str(line)
    return returnStr

  def toPointTuple(self):
    points = []
    for point in self.points:
      points.append(point.toTuple())
    return points

  def toLineTuple(self):
    lines = []
    for line in self.lines:
      lines.append(line.toTuple())
    return lines

  def isPolyLine(self,testLine):
    for line in self.lines:
      if line == testLine:
        return True
    return False

  def pointInside(self, point):
    return pointInsidePolygonLines(point, self.lines) and point not in self.points

  def lineInside(self, testLine):
    if self.pointInside(testLine.p1) and self.pointInside(testLine.p2):
      return True

    if (self.pointInside(testLine.p1) or self.pointInside(testLine.p2)) and self.lineIntersects(testLine):
      return True

    return False

  def lineIntersects(self, testLine):
    for line in self.lines:
      if rayTraceNoEndpoints(line.p1,line.p2,testLine) and line != testLine:
        return True

    return False


  def lineObstructs(self, testLine):
    # Line crosses inside
    if self.lineInside(testLine) and not self.isPolyLine(testLine):
      return True

    # Line intersects
    if self.lineIntersects(testLine):
      return True

    return False

  def overlapsPoly(self, poly):
    for line1 in self.lines:
      for line2 in poly.lines:
        if rayTraceNoEndpoints(line1.p1,line1.p2, line2) and line1 != line2:
          return True

    return False

  def unobstructed(self, points, lines, polys):
    for point in points:
      if self.pointInside(point):
        # print "Point inside"
        return False

    for line in lines:
      if self.lineObstructs(line):
        print "Line obstructs"
        return False

    for poly in polys:
      if self.overlapsPoly(poly):
        # print "Poly overlap"
        return False

    return True

  def combinePoly(self, otherPoly):
    # Check if polys are adjacent
    adjPoints = polygonsAdjacent(self.points, otherPoly.points)
    if adjPoints:
      # Combine two polys lines
      combinedPolyLines = self.lines
      combinedPolyLines.extend(otherPoly.lines)

      commonLine = (adjPoints[0],adjPoints[1])
      if commonLine in combinedPolyLines:
        combinedPolyLines = filter(lambda a: a != commonLine, combinedPolyLines)
      if reverseLine(commonLine) in combinedPolyLines:
        combinedPolyLines = filter(lambda a: a != reverseLine(commonLine), combinedPolyLines)

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

def createLineRepOfPolyPoints(points):
  lines = []
  last = None
  for p in points:
    if last != None:
      lines.append(Line(last, p))
    last = p
  lines.append(Line(points[len(points)-1], points[0]))
  return lines

def createPointRepOfPolyLines(lines):
  points = []
  startingPoint = lines[0].p1
  currentPoint = startingPoint
  coveredLines = []
  pointTrail = []

  stuck = 0

  while True:
    stuck += 1
    if stuck > 1000:
      print lines
      print coveredLines
      print currentPoint
      print startingPoint
      print pointTrail

    for line in lines:
      if line not in coveredLines:
        if line.p1 == currentPoint:
          points.append(currentPoint)
          coveredLines.append(line)
          pointTrail.append(currentPoint)
          currentPoint = line.p2

        elif line.p2 == currentPoint:
          points.append(currentPoint)
          coveredLines.append(line)
          pointTrail.append(currentPoint)
          currentPoint = line.p1

        if currentPoint == startingPoint:
          return points

def pointsToTuples(points):
  tuples = []
  for point in points:
    tuples.append(point.toTuple())
  return tuples

def linesToTuples(lines):
  tuples = []
  for line in lines:
    tuples.append(line.toTuple())
  return tuples

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
