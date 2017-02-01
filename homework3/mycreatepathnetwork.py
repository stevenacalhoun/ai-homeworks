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

  # polys = createNavMesh(world.getPoints(), world.getLinesWithoutBorders())
  # print str(len(polys)) + " Polys"
  # nodes = createPathNodes(polys)
  # print str(len(nodes)) + " Nodes"
  # # edges = createPathLines(nodes, world.getPoints(), world.getLinesWithoutBorders())
  # print str(len(edges)) + " Edges"
  #
  # for node in nodes:
  #   drawCross(world.debug, node, color=(0,0,255))

  ### YOUR CODE GOES ABOVE HERE ###
  return nodes, edges, polys

# Create navmesh
def createNavMesh(obstaclePoints, obstacleLines):
  # Create navmesh only out of triangles
  polys = createTriangleMesh(obstaclePoints, obstacleLines)

  # Combine triangles to higher order polygons
  while True:
    combinedPoly, poly1, poly2 = combinePolysOnce(polys)

    if combinedPoly != None:
      print "Combining"
      removePoly(poly1, polys)
      removePoly(poly2, polys)
      polys.append(combinedPoly)
    else:
      break

  return polys

# Create triangle mesh
def createTriangleMesh(obstaclePoints, obstacleLines):
  completedPoints = []
  tris = []

  # Continue until all points covered
  for point in obstaclePoints:

    # Create triangles around this point
    createTrianglesFromPoint(obstaclePoints, obstacleLines, point, tris)

  return tris

# Get all successors of a point
def getAllSuccessors(startPoint, obstaclePoints, obstacleLines):
  successors = []
  for point in obstaclePoints:
    if isSuccessor(startPoint, point, obstacleLines):
      successors.append(point)

  return successors

def createTrianglesFromPoint(obstaclePoints, obstacleLines, currentPoint, currentTris):
  coveredSuccessors = []
  tris = []
  successors = getAllSuccessors(currentPoint, obstaclePoints, obstacleLines)

  for successor1 in successors:
    # Start with an uncovered successor
    if successor1 not in coveredSuccessors:
      # Find a suitable second successor
      for successor2 in successors:
        if isSuccessor(successor1, successor2, obstacleLines):
          testTri = [currentPoint, successor1, successor2]

          # Make sure our test tri doesn't overlap any other triangle
          if unobstructedTri(testTri, obstaclePoints, currentTris):
            coveredSuccessors.append(successor1)
            coveredSuccessors.append(successor2)
            currentTris.append(testTri)

  return tris

def unobstructedTri(testTri, obstaclePoints, currentTris):
  for tri in currentTris:
    if polysOverlap(testTri, tri):
      return False

  for point in obstaclePoints:
    if pointInsidePolygonPoints(point, testTri) and point not in testTri:
      return False

  return True

# Check if two lines are successors
def isSuccessor(point1, point2, obstacleLines):
  # Lines through free space are okay
  if (rayTraceWorldNoEndPoints(point1, point2, obstacleLines) == None and point1 != point2):
    return True

  # Lines along obstacleLines are okay
  if (point1,point2) in obstacleLines:
    return True
  if (point2,point1) in obstacleLines:
    return True

  return False

# Combine triangles to higher order convex polys
def combinePolysOnce(polys):
  for poly1 in polys:
    for poly2 in polys:
      combinedPoly = combineTwoPolys(poly1, poly2)
      if combinedPoly != None:
        return combinedPoly, poly1, poly2
  return None, None, None

# def combineTwoPolys(poly1,poly2):
#   adjPoints = polygonsAdjacent(poly1,poly2)
#   if adjPoints:
#     combinedPoly = []
#     for point in poly1:
#       appendPointNoDuplicates(point, combinedPoly)
#     for point in poly2:
#       appendPointNoDuplicates(point, combinedPoly)
#
#     if isConvex(combinedPoly):
#       return combinedPoly
#     else:
#       return None
#
#   else:
#     return None

# Create path nodes from navmesh polys
def createPathNodes(polys):
  nodes = []

  # For every shared line between polys, add a path node at the midpoint
  for poly1 in polys:
    for line in createLineRepOfPolyPoints(poly1):
      appendPointNoDuplicates(getMidPoint(line[0],line[1]), nodes)

    # for poly2 in polys:
    #   print
    #   print poly1
    #   print poly2
    #   adjacentPoints = polygonsAdjacent(poly1, poly2)
    #   if adjacentPoints:
    #     print adjacentPoints
    #     appendPointNoDuplicates(getMidPoint(adjacentPoints[0],adjacentPoints[1]), nodes)

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
  if rayTraceWorldNoEndPoints(p1, p2, obstacleLines) != None:
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

def appendPointNoDuplicates(point, points):
  if point in points:
    return points
  else:
    return points.append(point)

def polysOverlap(poly1, poly2):
  poly1Lines = createLineRepOfPolyPoints(poly1)
  poly2Lines = createLineRepOfPolyPoints(poly2)
  for line1 in poly1Lines:
    for line2 in poly2Lines:
      if calculateIntersectPoint(line1[0], line1[1], line2[0], line2[1]) and not linesEqual(line1,line2) and not linesContainsCommonPoint(line1,line2):
        return True

  return False

def linesEqual(line1, line2):
  if line1 == line2:
    return True
  if line1 == reverseLine(line2):
    return True
  return False

def linesContainsCommonPoint(line1, line2):
  if line1[0] == line2[0] or line1[0] == line2[1]:
    return True
  if line1[1] == line2[0] or line1[1] == line2[1]:
    return True
  return False

def removePoly(deletedPoly, polys):
  polys.remove(deletedPoly)

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
        if line not in self.lines and reverseLine(line) not in self.lines:
          self.lines.append(line)

      # Convert to points
      self.points = createPointRepOfPolyLines(self.lines)

  def __eq__(self, otherPoly):
    if otherPoly == None:
      return False

    if len(self.lines) != len(otherPoly.lines):
      return False

    for line in self.lines:
      if line not in otherPoly.lines and reverseLine(line) not in otherPoly.lines:
        return False

    return True

  def __ne__(self, otherPoly):
    result = self.__eq__(otherPoly)
    return not result

  def isPolyLine(self,testLine):
    for line in self.lines:
      if linesEqual(line, testLine):
        return True
    return False

  def pointInside(self, point):
    return pointInsidePolygonLines(point, self.lines)

  def lineInside(self, testLine):
    if self.pointInside(testLine[0]) and self.pointInside(testLine[1]):
      return True

    if (self.pointInside(testLine[0]) or self.pointInside(testLine[1])) and self.lineIntersects(testLine):
      return True

    return False

  def lineIntersects(self, testLine):
    for line in self.lines:
      if rayTraceNoEndpoints(line[0],line[1],testLine) and not linesEqual(line, testLine):
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
        if rayTraceNoEndpoints(line1[0],line1[1], line2) and not linesEqual(line1,line2):
          return True

    return False

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
      lines.append((last, p))
    last = p
  lines.append((points[len(points)-1], points[0]))
  return lines

def createPointRepOfPolyLines(lines):
  points = []
  startingPoint = lines[0][0]
  currentPoint = startingPoint
  coveredLines = []
  while True:
    for line in lines:
      if line not in coveredLines:
        if line[0] == currentPoint:
          points.append(currentPoint)
          coveredLines.append(line)
          currentPoint = line[1]

        elif line[1] == currentPoint:
          points.append(currentPoint)
          coveredLines.append(line)
          currentPoint = line[0]

        if currentPoint == startingPoint:
          return points

def test():
  # No overlap
  poly1 = Polygon(points=[(0,0), (100,0), (0, 100)])
  poly2 = Polygon(lines=[((100,0),(0,100)), ((0,100),(100,100)), ((100,100),(100,0))])
  assert poly1.overlapsPoly(poly2) == False

  # No Overlap
  poly1 = Polygon(points=[(0,0), (100,0), (0, 100)])
  poly2 = Polygon(lines=[((100,0),(0,100)), ((0,100),(10,10)), ((10,10),(100,0))])
  assert poly1.overlapsPoly(poly2) == False

  # Overlap
  poly1 = Polygon(points=[(0,0), (100,0), (0, 100)])
  poly2 = Polygon(points=[(10,10), (200,200), (0, 100)])
  assert poly1.overlapsPoly(poly2) == True

  # Line test
  poly = Polygon(points=[(10,10), (110,10), (110, 110), (10,110)])
  assert poly.lineObstructs(((10,10),(110,10))) == False
  assert poly.lineObstructs(((10,10),(110,110))) == True
  assert poly.lineObstructs(((0,0),(10,10))) == False
  assert poly.lineObstructs(((10,10),(50,50))) == True
  assert poly.lineObstructs(((0,0),(50,50))) == True

  # Eq test
  poly1 = Polygon(points=[(0,0), (100,0), (0, 100)])
  poly2 = Polygon(points=[(0,0), (0, 100), (100,0)])
  assert (poly1==poly1) == True
  assert (poly1!=poly1) == False
  assert (poly1==poly2) == True
  assert (poly1!=poly2) == False

  # Combine test
  poly1 = Polygon(points=[(0,0), (100,0), (0, 100)])
  poly2 = Polygon(points=[(100,0),(0,100), (100,100)])
  combinedPoly = poly1.combinePoly(poly2)
  assert combinedPoly != None
