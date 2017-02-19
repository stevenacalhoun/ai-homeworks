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

from mycreatepathnetwork import *

### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the Floyd-Warshall algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
  ### YOUR CODE GOES BELOW HERE ###

  # # Convert world objects
  # nodePoints = pointTuplesToPoints(path)
  # worldPoints, worldLines = lineTuplesToLinesAndPoints(world.getLines())
  # agentPos = Point(pointTuple=agent.position)
  # destPoint = Point(pointTuple=dest)
  #
  # # Check for shortcut from start/goal
  # firstPointIdx = 0
  # lastPointIdx = len(nodePoints)-1
  # for i,node in enumerate(nodePoints):
  #   j = len(nodePoints) - i - 1
  #
  #   # Check from start
  #   pathLine = Line(agentPos, nodePoints[i])
  #   if pathLine.agentCanFollow(worldPoints, worldLines, agent.getMaxRadius()):
  #     firstPointIdx = i
  #
  #   # Check from goal
  #   pathLine = Line(destPoint, nodePoints[j])
  #   if pathLine.agentCanFollow(worldPoints, worldLines, agent.getMaxRadius()):
  #     lastPointIdx = j
  #
  # if firstPointIdx >= lastPointIdx:
  #   path = [path[firstPointIdx], destPoint.toTuple()]
  # else:
  #   path = path[firstPointIdx:lastPointIdx+1]

  ### YOUR CODE GOES BELOW HERE ###
  return path


### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
  ### YOUR CODE GOES BELOW HERE ###

  return False

  # Corner case
  if nav.path == None or nav.path == []:
    return False

  # Convert world objects
  worldPointObjects, worldLineObjects = lineTuplesToLinesAndPoints(nav.world.getLines())
  pathObjects = pointTuplesToPoints(nav.path)
  agentPositionObj = Point(pointTuple=nav.agent.position)
  destinationObj = Point(pointTuple=nav.destination)

  # Target in view
  pathLine = Line(agentPositionObj, destinationObj)
  if pathLine.agentCanFollow(worldPointObjects, worldLineObjects, agentWidth=nav.agent.getMaxRadius()+10):
    nav.setPath(None)
    nav.agent.moveToTarget(destinationObj.toTuple())
    return True

  # See if any future node is in view
  visibleNodeIdx = -1
  for i,node in enumerate(pathObjects):
    pathLine = Line(agentPositionObj, node)
    if pathLine.agentCanFollow(worldPointObjects, worldLineObjects, agentWidth=nav.agent.getMaxRadius()+10):
      visibleNodeIdx = i

  # Set trim path and set new target
  if visibleNodeIdx != -1:
    nav.setPath(pointsToTuples(pathObjects[visibleNodeIdx:]))
    nav.agent.moveToTarget(nav.path[0])
    return True

  ### YOUR CODE GOES ABOVE HERE ###
  return False

################################################################################################
# Custom Point class instead of tuples
################################################################################################
class Point(object):
  def __init__(self, x=None, y=None, pointTuple=None):
    if pointTuple == None:
      self.x = x
      self.y = y
    else:
      self.x = pointTuple[0]
      self.y = pointTuple[1]

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

  def __hash__(self):
    return hash((self.x, self.y))

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
  def __init__(self, p1=None, p2=None, lineTuple=None):
    if lineTuple == None:
      self.p1 = p1
      self.p2 = p2
    else:
      self.p1 = Point(pointTuple=lineTuple[0])
      self.p2 = Point(pointTuple=lineTuple[1])
    self.length = math.sqrt(math.pow(self.p2.x - self.p1.x,2) + math.pow(self.p2.y - self.p1.y,2))

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

  def draw(self, surface, color=(0,0,0), size=1):
    pygame.draw.line(surface, color, self.p1.toTuple(), self.p2.toTuple(), size)

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
  def agentCanFollow(self, worldPoints, worldLines, agentWidth=AGENT_WIDTH):
    # Intersection with any world line is obviously unfollowable
    if self.intersectsAny(worldLines):
      return False

    # Make sure the agent won't clip any obstacle points along a line
    for point in worldPoints:
      if minimumDistance([self.p1, self.p2], point) < agentWidth and self not in worldLines and point != self.p1 and point != self.p2:
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

def pointTuplesToPoints(pointTuples):
  points = []
  for pointTuple in pointTuples:
    p = Point(pointTuple=pointTuple)
    if p not in points:
      points.append(p)
  return points

def pointTuplesToPointsAndLines(pointTuples):
  points = pointTuplesToPoints(pointTuples)
  lines = []
  for i,p1 in enumerate(points):
    if i != 0:
      p2 = points[i-1]
      lines.append(Line(p1,p2))
  return points, lines

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

def lineTuplesToLines(lineTuples):
  points, lines = lineTuplesToLinesAndPoints(lineTuples)
  return lines

def lineTuplesToLinesAndPoints(lineTuples):
  points = []
  lines = []
  for line in lineTuples:
    p1 = Point(pointTuple=line[0])
    p2 = Point(pointTuple=line[1])
    if p1 not in points:
      points.append(p2)
    if p2 not in points:
      points.append(p2)
    lines.append(Line(p1=p1,p2=p2))
  return points, lines

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
