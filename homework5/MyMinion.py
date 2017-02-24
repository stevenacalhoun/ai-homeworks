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
waveCount = 1

minions = []

class MyMinion(Minion):

  def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
    Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
    self.states = [Idle]
    ### Add your states to self.states (but don't remove Idle)
    ### YOUR CODE GOES BELOW HERE ###
    self.states.append(AttackClosestTower)
    self.states.append(AttackBase)
    self.states.append(MoveToTarget)
    self.states.append(Attack)
    self.states.append(Shoot)

    global minionCount, waveCount

    # Defense team wave
    if waveCount == 2:
      self.team = "defend"

    # Otherwise a new attack team
    else:
      self.team = "attack"

    # Keep up with minion/wavecount
    minionCount += 1
    if minionCount % 3 == 0:
      print "Wave " + str(waveCount)
      waveCount += 1
    print "Minion Count: " + str(minionCount)

    updateMinions(self)

    ### YOUR CODE GOES ABOVE HERE ###

  def start(self):
    Minion.start(self)
    self.agent.changeState(Idle, self.agent)

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

    if self.team == "attack":
      self.team.changeState(MoveToTarget, self)
    else:
      self.changeState(Defend, self)

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

class Defend(State):

  def parseArgs(self, args):
    self.victim = args[0]

  def execute(self, delta = 0):
    print "Defend"

class Attack(State):
  def parseArgs(self, args):
    self.agent = args[0]

  def execute(self, delta = 0):
    # Towers are dead, attack base
    if towersDead(self.agent, self.agent.world):
      target = self.agent.world.getEnemyBases(self.agent.getTeam())[0]

    # Attack closest tower
    else:
      towers = self.agent.world.getEnemyTowers(self.agent.getTeam())
      closestDistance = INFINITY
      # Find closest tower
      for tower in towers:
        if distance(self.agent, tower.position) < closestDistance:
          closestDistance = distance(self.agent, tower.position)
          target = tower

    self.agent.changeState(MoveToTarget, self.agent, target)

# Move in range to a target
class MoveToTarget(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[0]
    self.agent.navigateTo(self.target.position)

  def execute(self, delta = 0):
    if targetInRange(self.agent, self.target.position):
      self.agent.changeState(Shoot, self.agent, self.target)

class SpreadOut(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[0]
    self.agent.navigateTo(self.target.position)

  def execute(self, delta = 0):
    global minions
    if targetInRange(self.agent, self.target.position) and minionOnTopOfOtherMinion(self.agent, minions):
      self.agent.changeState(Shoot, self.agent, self.target)

# Shoot until target dead
class Shoot(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[0]
    self.agent.stopMoving()
    self.agent.turnToFace(self.target.position)

  def execute(self, delta = 0):
    # Shoot until target dies
    if self.target.getHitpoints() > 0:
      self.agent.shoot()
    else:
      self.agent.changeState(Idle, self.agent)

# Target is in range of shooting
def targetInRange(agent, target):
  return distance(agent.position, target) < BULLETRANGE

# Both towers are dead
def towersDead(agent, world):
  for tower in world.getEnemyTowers(agent.getTeam()):
    if tower.getHitpoints() > 0:
      return False
  return True

def updateMinions(newMinion):
  global minions
  deadMinions = []
  minions.append(newMinion)
  for minion in minions:
    if minion.getHitpoints() <= 0:
      deadMinions.append(minion)

  for minion in deadMinions:
    minions.remove(minion)

def minionOnTopOfOtherMinion(minion, minions):
  for otherMinion in minions:
    if minion.position == otherMinion.position:
      return True
  return False
