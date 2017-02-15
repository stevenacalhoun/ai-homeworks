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

  if nav.path == None:
    return False

  if clearShot(nav.agent.position, nav.destination, nav.world.getLines(), nav.world.getPoints()):
    nav.setPath([])
    nav.agent.moveToTarget(nav.destination)
    return True

  visibleNode = -1
  for i,node in enumerate(nav.path):
    if clearShot(nav.agent.position, node, nav.world.getLines(), nav.world.getPoints()):
      visibleNodeIdx = i
      visibleNode = node

  if visibleNode != -1:
    nav.setPath(nav.path[visibleNodeIdx:])
    nav.agent.moveToTarget(visibleNode)
    return True

  ### YOUR CODE GOES ABOVE HERE ###
  return False

def clearShot(p1, p2, worldLines, worldPoints):
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
