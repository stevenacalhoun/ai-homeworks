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

  # visibleNode = -1
  # for i,node in enumerate(path):
  #   if clearShot(source, node, world.getLines(), world.getPoints(), agent):
  #     print i
  #     print path
  #     visibleNode = i
  #
  # if visibleNode != -1:
  #   path = path[visibleNode:]
  #   return path

  ### YOUR CODE GOES BELOW HERE ###
  return path


### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
  ### YOUR CODE GOES BELOW HERE ###

  # Corner case
  if nav.path == None:
    return False

  # Convert world objects
  worldPointObjects = []
  worldLineObjects = []
  for line in nav.world.getLines():
    p1 = Point(pointTuple=line[0])
    p2 = Point(pointTuple=line[1])
    if p1 not in worldLineObjects:
      worldPointObjects.append(p2)
    if p2 not in worldLineObjects:
      worldPointObjects.append(p2)
    worldLineObjects.append(Line(p1=p1,p2=p2))
  agentPositionObj = Point(pointTuple=nav.agent.position)
  destinationObj = Point(pointTuple=nav.destination)
  pathObjects = []
  for node in nav.path:
    pathObjects.append(Point(pointTuple=node))

  # Target in view
  pathLine = Line(agentPositionObj, destinationObj)
  if pathLine.agentCanFollow(worldPointObjects, worldLineObjects):
    nav.setPath([])
    nav.agent.moveToTarget(destinationObj.toTuple())
    return True

  # See if any future node is in view
  visibleNodeIdx = 0
  for i,node in enumerate(pathObjects):
    pathLine = Line(agentPositionObj, node)
    if pathLine.agentCanFollow(worldPointObjects, worldLineObjects):
      visibleNodeIdx = i

  # Set new target and trim path
  nav.setPath(pointsToTuples(pathObjects[visibleNodeIdx:]))
  nav.agent.moveToTarget(nav.path[0])
  return True

  ### YOUR CODE GOES ABOVE HERE ###
  return False
