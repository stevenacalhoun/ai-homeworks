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
defenderCount = 0
globalPrintStatus = False

class MyMinion(Minion):

  def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
    Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
    self.states = [Idle]
    ### Add your states to self.states (but don't remove Idle)
    ### YOUR CODE GOES BELOW HERE ###

    # Starting squad states
    self.states.append(Attack)
    self.states.append(Defend)

    # Defend states
    self.states.append(DefendMoveToLookout)
    self.states.append(DefendWaitForEnemy)

    # General states
    self.states.append(MoveToTarget)
    self.states.append(SpreadOut)
    self.states.append(Shoot)

    global minionCount, waveCount, defenderCount

    # Defense team wave
    if waveCount % 4 == 2 and defenderCount < 6:
      defenderCount += 1
      self.squad = "defend"

    # Otherwise a new attack team
    else:
      self.squad = "attack"

    # Keep up with minion/wavecount
    minionCount += 1
    if minionCount % 3 == 0:
      waveCount += 1
    if globalPrintStatus:
      print "Minion Count: " + str(minionCount)

    # Update minion array
    updateMinions(self)

    ### YOUR CODE GOES ABOVE HERE ###

  def start(self):
    Minion.start(self)
    self.changeState(Idle, self)

############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
  def parseArgs(self, args):
    self.agent = args[0]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Idle"

    State.enter(self, oldstate)
    # stop moving
    self.agent.stopMoving()

  def execute(self, delta = 0):
    State.execute(self, delta)
    # YOUR CODE GOES BELOW HERE ###

    if self.agent.squad == "attack":
      self.agent.changeState(Attack, self.agent)
    elif self.agent.squad == "defend":
      self.agent.changeState(Defend, self.agent)

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

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Taunt"

  def execute(self, delta = 0):
    if self.victim is not None:
      print "Hey " + str(self.victim) + ", I don't like you!"
    self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

# Post up to defend
class Defend(State):
  def parseArgs(self, args):
    self.victim = args[0]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Defend"

    if not gameOver(self.agent):
      self.enemies = enemiesInRange(self.agent, 300)

  def execute(self, oldstate):
    if not gameOverHandle(self.agent):
      if len(self.enemies):
        self.agent.changeState(MoveToTarget, self.agent, self.enemies[0], Shoot)
      else:
        self.agent.changeState(DefendMoveToLookout, self.agent)

# Attack closest tower or base
class Attack(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.over = False

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Attack"

    if not gameOver(self.agent):
      # Towers are dead, attack base
      if towersDead(self.agent, self.agent.world):
        self.target = self.agent.world.getEnemyBases(self.agent.getTeam())[0]

      # Attack closest tower
      else:
        towers = self.agent.world.getEnemyTowers(self.agent.getTeam())
        closestDistance = INFINITY
        # Find closest tower
        for tower in towers:
          if distance(self.agent.position, tower.position) < closestDistance:
            closestDistance = distance(self.agent.position, tower.position)
            self.target = tower


  def execute(self, oldstate):
    if not gameOverHandle(self.agent):
      self.agent.changeState(MoveToTarget, self.agent, self.target, Shoot)

# Move in range to a target
class DefendMoveToLookout(State):
  def parseArgs(self, args):
    self.agent = args[0]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Moving to defend"

    if not gameOver(self.agent):
      towers = self.agent.world.getTowersForTeam(self.agent.getTeam())

      # Defend on base, on 1 tower, or between 2 towers
      if len(towers) == 0:
        self.target = self.agent.world.getBaseForTeam(self.agent.getTeam()).position
      elif len(towers) == 1:
        self.target = towers[0].position
      elif len(towers) == 2:
        self.target = midpoint(towers[0].position, towers[1].position)

      self.agent.navigateTo(self.target)

  def execute(self, delta = 0):
    if not gameOverHandle(self.agent):
      if distance(self.agent.position, self.target) < 20:
        self.agent.stopMoving()
        self.agent.changeState(DefendWaitForEnemy, self.agent)

# Defend wait for an enemy
class DefendWaitForEnemy(State):
  def parseArgs(self, args):
    self.agent = args[0]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Wait for enemy"

  def execute(self, delta = 0):
    if not gameOverHandle(self.agent):
      enemies = enemiesInRange(self.agent, 300)
      if len(enemies):
        self.agent.changeState(MoveToTarget, self.agent, enemies[0], Shoot)

# Move in shooting range of a target
class MoveToTarget(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[1]
    self.nextState = args[2]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Moving to target"

    if not gameOver(self.agent):
      self.agent.navigateTo(self.target.position)

  def execute(self, delta = 0):
    if not gameOverHandle(self.agent):
      if targetInRange(self.agent, self.target.position):
        self.agent.stopMoving()
        self.agent.changeState(self.nextState, self.agent, self.target)

# Make sure agent is on top of others
class SpreadOut(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[1]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Spreading out"

    if not gameOver(self.agent):
      self.agent.navigateTo(self.target.position)

  def enter(self, oldstate):
    if gameOver(self.agent):
      return

  def execute(self, delta = 0):
    global minions
    if not gameOverHandle(self.agent):
      if targetInRange(self.agent, self.target.position) and not minionOnTopOfOtherMinion(self.agent, minions):
        self.agent.stopMoving()
        self.agent.changeState(Shoot, self.agent, self.target)

# Shoot until target dead
class Shoot(State):
  def parseArgs(self, args):
    self.agent = args[0]
    self.target = args[1]

  def enter(self, oldstate):
    if printStatus(self.agent):
      print "Shooting"

    if not gameOver(self.agent):
      self.agent.stopMoving()
      self.agent.turnToFace(self.target.position)

  def execute(self, delta = 0):
    if not gameOverHandle(self.agent):
      if targetInRange(self.agent, self.target.position):
        # Shoot until target dies
        if self.target.getHitpoints() > 0:
          self.agent.turnToFace(self.target.position)
          self.agent.shoot()
        else:
          self.agent.changeState(Idle, self.agent)

# Target is in range of shooting
def targetInRange(agent, target, range=BULLETRANGE):
  return distance(agent.position, target) < range

# Both towers are dead
def towersDead(agent, world):
  for tower in world.getEnemyTowers(agent.getTeam()):
    if tower.getHitpoints() > 0:
      return False
  return True

# Update minion counts and array of alive minions
def updateMinions(newMinion):
  global minions
  deadMinions = []
  minions.append(newMinion)
  for minion in minions:
    if minion.getHitpoints() <= 0:
      deadMinions.append(minion)

  for minion in deadMinions:
    minions.remove(minion)

# Check if minion is on top of another minion
def minionOnTopOfOtherMinion(minion, minions):
  for otherMinion in minions:
    if minion.position == otherMinion.position and minion != otherMinion:
      return True
  return False

# Midpoint of two points
def midpoint(p1,p2):
  return ((p1[0]+p2[0])/2.0, (p1[1]+p2[1])/2.0)

# Check if any enemies are in range
def enemiesInRange(agent, range):
  enemies = []
  for enemy in agent.world.getEnemyNPCs(agent.getTeam()):
    if targetInRange(agent, enemy.position, range=range):
      enemies.append(enemy)
  return enemies

# 1 base remaining means the game is over
def gameOver(agent):
  return len(agent.world.getBases()) == 1

# Game over check and change agent states and squad
def gameOverHandle(agent):
  if gameOver(agent):
    agent.squad = "idle"
    agent.changeState(Idle, agent)
    return True
  return False

# Helper to print states
def printStatus(agent):
  return globalPrintStatus and False
