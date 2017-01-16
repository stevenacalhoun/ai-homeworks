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
from gridnavigator import *

w1_polygons = [[(628, 698), (582, 717), (549, 688), (554, 546), (676, 548)],
[(942, 484), (811, 396), (843, 299), (921, 300)],
[(457, 422), (371, 506), (300, 515), (300, 400), (454, 350)]]

w2_polygons = [[(223.0, 137.0), (212.5, 169), (185, 189), (151, 189), (123.5, 169), (113.0, 137.0), (123.5, 104.5), (151, 84.5), (185, 84.5), (212.5, 104.5)],
[(700, 160), (630.0, 143), (650, 100)],
[(260.0, 422.0), (205, 555), (72, 610.0), (72, 234.0), (205, 289)],
[(515.0, 216.0), (488, 289), (421, 328), (344.0, 315), (294, 255), (294, 177), (344, 117), (421, 104), (488, 143)],
[(773.0, 558.0), (724, 660.5), (613.5, 687), (523, 618), (520, 504), (607, 430.5), (718.5, 451)],
[(100.0, 14.0), (130, 14.5), (80.5, 50)],
[(586.0, 57.0), (570.5, 94.5), (533.0, 110.0), (495.5, 94.5), (480.0, 57), (495.5, 19.5), (533.0, 4.0), (570.5, 19.5)]]

w3_polygons = [[(430.0, 847.0), (399.5, 889), (350.5, 873), (350.5, 821), (399.5, 805)],
[(242.0, 796.0), (187.0, 851.0), (132.0, 796.0), (187.0, 741.0)],
[(602.0, 396.0), (547.0, 451.0), (492.0, 396.0), (547.0, 341.0)],
[(254.0, 605.0), (230.0, 646.5), (182.0, 646.5), (158.0, 605.0), (182, 563.5), (230.0, 563.5)],
[(391.0, 264.0), (370, 307.5), (323, 319), (285, 289.5), (284, 241), (320.5, 210), (368, 218.5)]]


worlds = [
  {
    "name": "World 1",
    "polygons": w1_polygons,
    "dimensions": [WORLD, SCREEN]
  },
  {
    "name": "World 2",
    "polygons": w2_polygons,
    "dimensions": [(768,768), (768,768)]
  },
  {
    "name": "World 3",
    "polygons": w3_polygons,
    "dimensions": [(768,1024), (768,1024)]
  }
]

def main():
  for world in worlds:
    testWorld(world)

def createWorld(seed, worldSize, screenSize, polygons):
  nav = GreedyGridNavigator()

  world = GameWorld(seed, worldSize, screenSize)
  agent = Agent(AGENT, (screenSize[0]/2, screenSize[1]/2), 0, SPEED, world)
  world.setPlayerAgent(agent)
  agent.setNavigator(nav)
  world.initializeTerrain(polygons, (255, 0, 0), 4, TREE)
  nav.setWorld(world)
  world.initializeRandomResources(NUMRESOURCES)
  world.debugging = True

  return world, nav

def testWorld(worldParams):
  print "Testing World " + worldParams["name"]
  world, nav = createWorld(SEED, worldParams["dimensions"][0], worldParams["dimensions"][1], worldParams["polygons"])

  obstacleError = 0
  borderError = 0

  linesWithoutBorders = world.getLinesWithoutBorders();

  for row in xrange(nav.dimensions[1]):
    for col in xrange(nav.dimensions[0]):
      if nav.grid[col][row]:
        # Get corners of the space
        topL = ((col+0)*nav.cellSize, (row+0)*nav.cellSize)
        topR = ((col+1)*nav.cellSize, (row+0)*nav.cellSize)
        botL = ((col+0)*nav.cellSize, (row+1)*nav.cellSize)
        botR = ((col+1)*nav.cellSize, (row+1)*nav.cellSize)

        # Lines of cell
        cellLines = [(topL, topR), (topR, botR), (botR, botL), (botL, topL)]

        for cellLine in  cellLines:
          for worldLineNum, line in enumerate(world.getLines()):
            if calculateIntersectPoint(line[0], line[1], cellLine[0], cellLine[1]):
              if line not in linesWithoutBorders:
                borderError += 1
              else:
                obstacleError +=1

  print worldParams["name"] + ": " + str(borderError) + " border errors"
  print worldParams["name"] + ": " + str(obstacleError) + " obstacle errors"
  print

if __name__ == "__main__":
  main()
