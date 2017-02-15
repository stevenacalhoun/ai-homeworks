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
from mynavigatorhelpers import *

import time
globalWorld = None

###############################
### AStarNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
class AStarNavigator(NavMeshNavigator):

  def __init__(self):
    NavMeshNavigator.__init__(self)

  ### Create the pathnode network and pre-compute all shortest paths along the network.
  ### self: the navigator object
  ### world: the world object
  def createPathNetwork(self, world):
    global globalWorld

    globalWorld = world
    self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
    return None

  ### Finds the shortest path from the source to the destination using A*.
  ### self: the navigator object
  ### source: the place the agent is starting from (i.e., it's current location)
  ### dest: the place the agent is told to go to
  def computePath(self, source, dest):
    ### Make sure the next and dist matricies exist
    if self.agent != None and self.world != None:
      self.source = source
      self.destination = dest

      ### Step 1: If the agent has a clear path from the source to dest, then go straight there.
      ###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
      ###   Tell the agent to move to dest
      if clearShot(source, dest, self.world.getLines(), self.world.getPoints(), self.agent):
        self.agent.moveToTarget(dest)

      ### Step 2: If there is an obstacle, create the path that will move around the obstacles.
      ###   Find the pathnodes closest to source and destination.
      ###   Create the path by traversing the self.next matrix until the pathnode closes to the destination is reached
      ###   Store the path by calling self.setPath()
      ###   Tell the agent to move to the first node in the path (and pop the first node off the path)
      else:
        start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
        end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
        if start != None and end != None:
          print len(self.pathnetwork)
          newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
          print len(newnetwork)
          closedlist = []
          path, closedlist = astar(start, end, newnetwork)
          if path is not None and len(path) > 0:
            path = shortcutPath(source, dest, path, self.world, self.agent)
            self.setPath(path)
            if self.path is not None and len(self.path) > 0:
              first = self.path.pop(0)
              self.agent.moveToTarget(first)
    return None

  ### Called when the agent gets to a node in the path.
  ### self: the navigator object
  def checkpoint(self):
    myCheckpoint(self)
    return None

  ### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
  ### This function should update the path and return True if the path was updated.
  def smooth(self):
    return mySmooth(self)

  def update(self, delta):
    myUpdate(self, delta)

def unobstructedNetwork(network, worldLines):
  newnetwork = []
  for l in network:
    hit = rayTraceWorld(l[0], l[1], worldLines)
    if hit == None:
      newnetwork.append(l)
  return newnetwork

def astar(init, goal, network):
  global globalWorld
  path = []

  closedSet = []
  openSet = []
  ### YOUR CODE GOES BELOW HERE ###

  initPoint = Point(init[0],init[1])
  goalPoint = Point(goal[0],goal[1])
  pathPoints = []
  pathLines = []

  openSet = [initPoint]

  for line in network:
    p1 = Point(line[0][0],line[0][1])
    p2 = Point(line[1][0],line[1][1])
    if p1 not in pathPoints:
      pathPoints.append(p1)
    if p2 not in pathPoints:
      pathPoints.append(p2)

    line = Line(p1,p2)
    if line not in pathLines:
      pathLines.append(line)

  cameFrom = {}

  # Set all initial values to infinity
  gScore = {}
  fScore = {}
  for node in pathPoints:
    gScore[node] = INFINITY
    fScore[node] = INFINITY
  fScore[initPoint] = distance(initPoint.toTuple(), goalPoint.toTuple())
  gScore[initPoint] = 0
  print "GOAL"
  print goalPoint

  while openSet is not []:
    # Find node with lowest fScore in openSet
    lowestScore = INFINITY
    for node in fScore:
      if node in openSet and fScore[node] < lowestScore:
        current = node
        lowestScore = fScore[node]

    # We've reached the goal, construct path and break
    if current == goalPoint:
      pathNodes = constructPath(cameFrom, current)
      break

    # Close curent point
    openSet.remove(current)
    closedSet.append(current)

    # Check all neighbors of current node
    for neighbor in getNeighbors(current, pathLines):
      # Only check non-closed nodes
      if neighbor not in closedSet:
        # Caclulate score
        tentative_gScore = gScore[current] + distance(current.toTuple(), neighbor.toTuple())

        # Neighbor is new to openSet
        if neighbor not in openSet:
          openSet.append(neighbor)

          cameFrom[neighbor] = current
          gScore[neighbor] = tentative_gScore
          fScore[neighbor] = gScore[neighbor] + distance(neighbor.toTuple(), goalPoint.toTuple())

        # Neighbor is in openSet and has a better gScore
        elif tentative_gScore < gScore[neighbor]:
          cameFrom[neighbor] = current
          gScore[neighbor] = tentative_gScore
          fScore[neighbor] = gScore[neighbor] + distance(neighbor.toTuple(), goalPoint.toTuple())

  # Convert back to tuples
  path = pointsToTuples(pathNodes)
  closed = pointsToTuples(closedSet)

  ### YOUR CODE GOES ABOVE HERE ###
  return path, closed

# Get all neighbors of a node
def getNeighbors(node, pathLines):
  neighbors = []
  for line in pathLines:
    if line.p1 == node:
      neighbors.append(line.p2)
    elif line.p2 == node:
      neighbors.append(line.p1)

  return neighbors

# Construct a path from A* data structures
def constructPath(cameFrom, current):
  total_path = [current]
  while current in cameFrom:
    current = cameFrom[current]
    total_path.append(current)
  total_path.reverse()
  return total_path

def myUpdate(nav, delta):
  ### YOUR CODE GOES BELOW HERE ###

  ### YOUR CODE GOES ABOVE HERE ###
  return None

def myCheckpoint(nav):
  ### YOUR CODE GOES BELOW HERE ###

  ### YOUR CODE GOES ABOVE HERE ###
  return None

### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
  ### YOUR CODE GOES BELOW HERE ###

  # Convert world objects
  worldPointObjects = []
  for point in worldPoints:
    p = Point(pointTuple=point)
    if p not in worldPointObjects:
      worldPointObjects.append(p)
  worldLineObjects = []
  lineObj = Line(lineTuple=(p1,p2))
  for line in worldLines:
    worldLineObjects.append(Line(lineTuple=line))

  pathLine = Line(lineTuple=(p1,p2))

  return pathLine.agentCanFollow(worldPointObjects, worldLineObjects) and not pathLine.intersectsAny(worldLines)
