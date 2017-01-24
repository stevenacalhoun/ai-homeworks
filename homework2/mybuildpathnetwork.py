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

# Creates the pathnetwork as a list of lines between all pathnodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
  lines = []
  ### YOUR CODE GOES BELOW HERE ###

  # Check each node
  for parentNode in pathnodes:
    # Check each node for each node
    for childNode in pathnodes:
      # Skip itself
      if parentNode != childNode:
        # Add line if unobstructed
        if lineUnobstructed(parentNode, childNode, world) and (lineInList(parentNode, childNode, lines) == False):
          lines.append([parentNode, childNode])

  ### YOUR CODE GOES ABOVE HERE ###
  return lines

# Check if line is unobstructed
def lineUnobstructed(p1, p2, world):
  # Ensure the line between the tow points doesn't intersect any object lines
  if rayTraceWorld(p1, p2, world.getLines()) != None:
    return False

  # Make sure the agent won't clip any obstacle points along a line
  for point in world.getPoints():
    ## This distance can be modified
    if minimumDistance([p1,p2], point) < 35.0:
      return False

  return True

def lineInList(p1,p2,lines):
  for line in lines:
    if (samePoint(p1,line[0]) and samePoint(p2,line[1])) or (samePoint(p1,line[1]) and samePoint(p2,line[0])):
      return True
  return False

def samePoint(p1, p2):
  return distance(p1,p2) == 0
