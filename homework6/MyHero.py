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
from moba2 import *
from behaviortree import *
from mybehaviors import *

##############################################################
### MyHero

class MyHero(Hero, BehaviorTree):

  def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
    Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)
    BehaviorTree.__init__(self)

  def update(self, delta):
    Hero.update(self, delta)
    BehaviorTree.update(self, delta)
    # writeText(self)
    setText(self)

  def start(self):
    # Build the tree
    spec = treeSpec(self)
    if spec is not None and (isinstance(spec, list) or isinstance(spec, tuple)):
      self.buildTree(spec)
    else:
      self.setTree(myBuildTree(self))
    # Start the agent
    Hero.start(self)
    BehaviorTree.start(self)

  def stop(self):
    Hero.stop(self)
    BehaviorTree.stop(self)

def setText(hero):
  hero.world.textLines = []
  hero.world.textLines.append(hero.world.myfont.render("Health: " + str(hero.hitpoints), 0, (0,0,0)))
  hero.world.textLines.append(hero.world.myfont.render("Level: " + str(hero.level), 0, (0,0,0)))
  if '1' in hero.world.score:
    hero.world.textLines.append(hero.world.myfont.render("Team 1 score: " + str(hero.world.score['1']), 0, (0,0,0)))
  else:
    hero.world.textLines.append(hero.world.myfont.render("Team 1 score: 0", 0, (0,0,0)))

  if '2' in hero.world.score:
    hero.world.textLines.append(hero.world.myfont.render("Team 2 score: " + str(hero.world.score['2']), 0, (0,0,0)))
  else:
    hero.world.textLines.append(hero.world.myfont.render("Team 2 score: 0", 0, (0,0,0)))
