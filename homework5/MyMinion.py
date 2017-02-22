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
from moba import *

import random

minionCount = 0

class MyMinion(Minion):

  def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
    Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
    self.states = [Idle]
    ### Add your states to self.states (but don't remove Idle)
    ### YOUR CODE GOES BELOW HERE ###
    self.states.append(AttackClosestTower)
    self.states.append(AttackBase)
    self.states.append(Attack)
    self.states.append(Shoot)

    global minionCount
    minionCount += 1
    print "Minion Count: " + str(minionCount)

    ### YOUR CODE GOES ABOVE HERE ###

  def start(self):
    Minion.start(self)
    self.changeState(Attack, self)

############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
  def parseArgs(self, args):
    self.agent = args[0]

  def enter(self, oldstate):
    State.enter(self, oldstate)
    # stop moving
    self.agent.stopMoving()

  def execute(self, delta = 0):
    State.execute(self, delta)
    ### YOUR CODE GOES BELOW HERE ###

    self.agent.changeState(Attack, self.agent)

    ### YOUR CODE GOES ABOVE HERE ###
    return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

  def parseArgs(self, args):
    self.victim = args[0]

  def execute(self, delta = 0):
    if self.victim is not None:
      print "Hey " + str(self.victim) + ", I don't like you!"
    self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

class Attack(State):
  def parseArgs(self, args):
    self.agent = args[0]

  def execute(self, delta = 0):
    if towersDead(self.agent, self.agent.world):
      self.agent.changeState(AttackBase, self.agent, self.agent.world.getEnemyBases(self.agent.getTeam())[0])
    else:
      self.agent.changeState(AttackClosestTower, self.agent, self.agent.world.getEnemyBases(self.agent.getTeam())[0])


class AttackClosestTower(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[1]
    self.agent.navigateTo(self.target.position)

  def execute(self, delta = 0):
    # Get all visible towers
    visibleTowers = self.agent.getVisibleType(Tower)
    if len(visibleTowers) > 0:
      # See if any visible tower is in range
      for visibleTower in visibleTowers:
        # Shoot tower if in range
        if targetInRange(self.agent, visibleTower.position) and visibleTower.team != self.agent.getTeam():
          self.agent.changeState(Shoot, self.agent, visibleTower)

class AttackBase(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[1]
    self.agent.navigateTo(self.target.position)

  def execute(self, delta = 0):
    if targetInRange(self.agent, self.target.position):
      self.agent.changeState(Shoot, self.agent, self.target)

class Shoot(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[1]
    self.agent.stopMoving()
    self.agent.turnToFace(self.target.position)

  def execute(self, delta = 0):
    # Shoot until target dies
    if self.target.getHitpoints() > 0:
      self.agent.shoot()
    else:
      self.agent.changeState(Idle, self.agent)

def targetInRange(agent, target):
  return distance(agent.position, target) < BULLETRANGE

def towersDead(agent, world):
  for tower in world.getEnemyTowers(agent.getTeam()):
    if tower.getHitpoints() > 0:
      return False
  return True
