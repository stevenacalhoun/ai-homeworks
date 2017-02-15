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

  # Convert world objects
  nodePoints = pointTuplesToPoints(path)
  worldPoints, worldLines = lineTuplesToLinesAndPoints(world.getLines())
  agentPos = Point(pointTuple=agent.position)
  destPoint = Point(pointTuple=dest)

  # Check for shortcut from start/goal
  firstPointIdx = 0
  lastPointIdx = len(nodePoints)-1
  for i,node in enumerate(nodePoints):
    # Check from start
    pathLine = Line(agentPos, nodePoints[i])
    if pathLine.agentCanFollow(worldPoints, worldLines, agent.getMaxRadius()):
      firstPointIdx = i

    # Check from goal
    j = len(nodePoints) - i - 1
    pathLine = Line(destPoint, nodePoints[j])
    if pathLine.agentCanFollow(worldPoints, worldLines, agent.getMaxRadius()):
      lastPointIdx = j

  if firstPointIdx >= lastPointIdx:
    path = [path[firstPointIdx]]
  else:
    path = path[firstPointIdx:lastPointIdx+1]

  ### YOUR CODE GOES BELOW HERE ###
  return path


### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
  ### YOUR CODE GOES BELOW HERE ###

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
