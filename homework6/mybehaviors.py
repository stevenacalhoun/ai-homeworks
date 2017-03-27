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
from btnode import *

###########################
### SET UP BEHAVIOR TREE


def treeSpec(agent):
  myid = str(agent.getTeam())
  spec = None
  ### YOUR CODE GOES BELOW HERE ###

  return TREE

  ### YOUR CODE GOES ABOVE HERE ###
  return spec

def myBuildTree(agent):
  myid = str(agent.getTeam())
  root = None
  ### YOUR CODE GOES BELOW HERE ###

  ### YOUR CODE GOES ABOVE HERE ###
  return root

### Helper function for making BTNodes (and sub-classes of BTNodes).
### type: class type (BTNode or a sub-class)
### agent: reference to the agent to be controlled
### This function takes any number of additional arguments that will be passed to the BTNode and parsed using BTNode.parseArgs()
def makeNode(type, agent, *args):
  node = type(agent, args)
  return node

###############################
### BEHAVIOR CLASSES:


##################
### Taunt
###
### Print disparaging comment, addressed to a given NPC
### Parameters:
###   0: reference to an NPC
###   1: node ID string (optional)

class Taunt(BTNode):

  ### target: the enemy agent to taunt

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.target = None
    # First argument is the target
    if len(args) > 0:
      self.target = args[0]
    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def execute(self, delta = 0):
    ret = BTNode.execute(self, delta)
    if self.target is not None:
      print "Hey", self.target, "I don't like you!"
    return ret

##################
### MoveToTarget
###
### Move the agent to a given (x, y)
### Parameters:
###   0: a point (x, y)
###   1: node ID string (optional)

class MoveToTarget(BTNode):

  ### target: a point (x, y)

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.target = None
    # First argument is the target
    if len(args) > 0:
      self.target = args[0]
    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def enter(self):
    BTNode.enter(self)
    self.agent.navigateTo(self.target)

  def execute(self, delta = 0):
    ret = BTNode.execute(self, delta)
    if self.target == None:
      # failed executability conditions
      print "exec", self.id, "false"
      return False
    elif distance(self.agent.getLocation(), self.target) < self.agent.getRadius():
      # Execution succeeds
      print "exec", self.id, "true"
      return True
    else:
      # executing
      return None
    return ret

##################
### Retreat
###
### Move the agent back to the base to be healed
### Parameters:
###   0: percentage of hitpoints that must have been lost to retreat
###   1: node ID string (optional)


class Retreat(BTNode):

  ### percentage: Percentage of hitpoints that must have been lost

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.percentage = 0.5
    # First argument is the factor
    if len(args) > 0:
      self.percentage = args[0]
    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def enter(self):
    BTNode.enter(self)
    self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())

  def execute(self, delta = 0):
    shootWhileRunning(self.agent)
    handleBullet(self.agent)
    handleAOEFire(self.agent)

    ret = BTNode.execute(self, delta)
    if self.agent.getHitpoints() == self.agent.getMaxHitpoints():
      # Exection succeeds
      print "exec", self.id, "true"
      return True
    elif self.agent.getHitpoints() > self.agent.getMaxHitpoints() * self.percentage:
      # fail executability conditions
      print "exec", self.id, "false"
      return False
    else:
      # executing
      return None
    return ret


class Chase(BTNode):

  ### target: the minion to chase
  ### timer: how often to replan

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.target = None
    self.timer = 50

    # First argument is the target type
    if len(args) > 0:
      self.targetType = args[0]

    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def enter(self):
    BTNode.enter(self)
    self.timer = 50
    enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())

    if len(enemies) > 0:
      if self.targetType == "Hero":
        self.target = getEnemyHero(self.agent)
      else:
        for e in enemies:
          best = None
          dist = 0
          if isinstance(e, Minion):
            d = distance(self.agent.getLocation(), e.getLocation())
            if best == None or d < dist:
              best = e
              dist = d
        self.target = best

    if self.target is not None:
      navTarget = self.chooseNavigationTarget()
      if navTarget is not None:
        if not self.targetInRange():
          self.agent.navigateTo(navTarget)

  def execute(self, delta = 0):
    shootWhileRunning(self.agent)
    handleBullet(self.agent)
    handleAOEFire(self.agent)

    dodgeLocationLeft, dodgeLocationRight = getDodgePositions(self.agent)
    drawDodgePositions(self.agent, [dodgeLocationLeft, dodgeLocationRight])

    # Have an advantage
    if levelAdvantage(self.agent, 2):
      print "exec", self.id, "fail"
      self.reset()
      return False

    ret = BTNode.execute(self, delta)
    if self.target == None or self.target.isAlive() == False:
      # failed execution conditions
      print "exec", self.id, "false"
      self.reset()
      return False
    elif self.targetInRange():
      # succeeded
      print "exec", self.id, "true"
      self.reset()
      return True
    else:
      # executing
      self.timer = self.timer - 1
      if self.timer <= 0:
        self.timer = 50
        navTarget = self.chooseNavigationTarget()
        if navTarget is not None:
          self.agent.navigateTo(navTarget)
      return None
    return ret

  def targetInRange(self):
    return distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE

  def chooseNavigationTarget(self):
    if self.target is not None:
      return self.target.getLocation()
    else:
      return None

def getEnemyHero(agent):
  enemies = agent.world.getEnemyNPCs(agent.getTeam())

  for e in enemies:
    if isinstance(e, Hero):
      return e
  return None

##################
### KillMinion
###
### Kill the closest minion. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class Kill(BTNode):

  ### target: the minion to shoot
  killCount = 0

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.target = None
    # First argument is the target type
    if len(args) > 0:
      self.targetType = args[0]

    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def enter(self):
    self.killCount = 0
    BTNode.enter(self)
    self.agent.stopMoving()
    enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
    if len(enemies) > 0:
      best = None
      dist = 0
      for e in enemies:
        if self.targetType == "Hero":
          if isinstance(e, Hero):
            d = distance(self.agent.getLocation(), e.getLocation())
            if best == None or d < dist:
              best = e
              dist = d
        else:
          if isinstance(e, Minion):
            d = distance(self.agent.getLocation(), e.getLocation())
            if best == None or d < dist:
              best = e
              dist = d
      self.target = best

  def execute(self, delta = 0):
    # shootWhileRunning(self.agent)
    handleBullet(self.agent)
    handleAOEFire(self.agent)

    self.killCount += 1
    if self.killCount > 1000:
      self.reset()
      return False

    dodgeLocationLeft, dodgeLocationRight = getDodgePositions(self.agent)
    drawDodgePositions(self.agent, [dodgeLocationLeft, dodgeLocationRight])

    ret = BTNode.execute(self, delta)
    if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
      # failed executability conditions
      print "exec", self.id, "false"
      self.reset()
      return False
    elif self.target.isAlive() == False:
      # succeeded
      print "exec", self.id, "true"
      self.reset()
      return True
    else:
      # executing
      self.shootAtTarget()
      return None
    return ret

  def shootAtTarget(self):
    if self.agent is not None and self.target is not None:
      leadShootTarget(self.agent, self.target)


##################
### HitpointDaemon
###
### Only execute children if hitpoints are above a certain threshold.
### Parameters:
###   0: percentage of hitpoints that must have been lost to fail the daemon check
###   1: node ID string (optional)


class HitpointDaemon(BTNode):

  ### percentage: percentage of hitpoints that must have been lost to fail the daemon check

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.percentage = 0.5
    # First argument is the factor
    if len(args) > 0:
      self.percentage = args[0]
    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def execute(self, delta = 0):
    ret = BTNode.execute(self, delta)
    if self.agent.getHitpoints() < self.agent.getMaxHitpoints() * self.percentage:
      # Check failed
      print "exec", self.id, "fail"
      return False
    else:
      # Check didn't fail, return child's status
      return self.getChild(0).execute(delta)
    return ret

##################
### BuffDaemon
###
### Only execute children if agent's level is significantly above enemy hero's level.
### Parameters:
###   0: Number of levels above enemy level necessary to not fail the check
###   1: node ID string (optional)

class BuffDaemon(BTNode):

  ### advantage: Number of levels above enemy level necessary to not fail the check

  def parseArgs(self, args):
    BTNode.parseArgs(self, args)
    self.advantage = 0
    # First argument is the advantage
    if len(args) > 0:
      self.advantage = args[0]
    # Second argument is the node ID
    if len(args) > 1:
      self.id = args[1]

  def execute(self, delta = 0):
    ret = BTNode.execute(self, delta)
    hero = None
    # Get a reference to the enemy hero
    if levelAdvantage(self.agent, self.advantage):
      return self.getChild(0).execute(delta)
    else:
      print "exec", self.id, "fail"
      return False
    return ret

def levelAdvantage(agent, advantage):
  hero = None
  # Get a reference to the enemy hero
  enemies = agent.world.getEnemyNPCs(agent.getTeam())
  for e in enemies:
    if isinstance(e, Hero):
      hero = e
      break
  return hero != None and agent.level >= (hero.level + advantage)

# Bullet is nearby
def nearbyBullet(agent):
  # Get all visible bullets
  visbleBullets = agent.getVisibleType(Bullet)
  bulletNear = False

  # Check all visible bullets
  for bullet in visbleBullets:
    if bullet.owner.getTeam() != agent.getTeam() and distance(agent.getLocation(), bullet.getLocation()) < 40:
      return bullet

  return None

def shouldDodge(agent):
  if not agent.candodge:
    return None
  return nearbyBullet(agent)

def handleBullet(agent):
  bullet = shouldDodge(agent)
  if bullet:
    print "Need to dodge"
    smartDodge(agent, bullet)
    return True

  return False

def smartDodge(agent, bullet):
  bulletVector = (agent.getLocation()[0] - bullet.position[0], agent.getLocation()[1] - bullet.position[1])

  leftDodgeAngle, rightDodgeAngle = getDodgeAngle(agent, inComingVector=bulletVector)
  dodgeLocationLeft, dodgeLocationRight = getDodgePositions(agent, inComingVector=bulletVector)

  drawDodgePositions(agent, [dodgeLocationLeft,dodgeLocationRight])
  # a = None
  # while a == None:
  #   a = raw_input("Pausing: ")

  bestPosition = dodgeLocationLeft
  bestAngle = leftDodgeAngle

  secondaryPosition = dodgeLocationRight
  secondaryAngle = rightDodgeAngle

  if agent.moveTarget != None:
    moveVector = (agent.moveTarget[0] - agent.getLocation()[0], agent.moveTarget[1] - agent.getLocation()[1])
    currentMoveAngle = getAngleVector(moveVector)

    bestAngle = closestAngle(currentMoveAngle, leftDodgeAngle, rightDodgeAngle)

    if bestAngle == 0:
      bestPosition = dodgeLocationLeft
      bestAngle = leftDodgeAngle

      secondaryPosition = dodgeLocationRight
      secondaryAngle = rightDodgeAngle
    else:
      bestPosition = dodgeLocationRight
      bestAngle = rightDodgeAngle

      secondaryPosition = dodgeLocationLeft
      secondaryAngle = leftDodgeAngle

  if collisionFree(agent, bestPosition):
    agent.dodge(angle=bestAngle)
  elif collisionFree(agent, secondaryPosition):
    agent.dodge(angle=secondaryAngle)
  else:
    return

def closestAngle(angle, a, b):
  aDifference = angle - a
  bDifference = angle - b

  if abs(aDifference) < abs(bDifference):
    return 0
  else:
    return 1

# Get two postions to jump
def getDodgePositions(agent, inComingVector=None):
  leftAngle, rightAngle = getDodgeAngle(agent, inComingVector=inComingVector)

  dodgeLocation = ((math.cos(math.radians(leftAngle))) * agent.getRadius() * 1.5, (-math.sin(math.radians(leftAngle))) * agent.getRadius() * 1.5)
  dodgeLocationRight = (agent.getLocation()[0] + dodgeLocation[0], agent.getLocation()[1] + dodgeLocation[1])
  dodgeLocationLeft = (agent.getLocation()[0] - dodgeLocation[0], agent.getLocation()[1] - dodgeLocation[1])

  return dodgeLocationLeft, dodgeLocationRight

def getDodgeAngle(agent, inComingVector=None):
  if inComingVector != None:
    angle = getAngleVector((-inComingVector[1], inComingVector[0]))
  else:
    angle = agent.orientation - 90

  return angle - 180, angle

def collisionFree(agent,position):
  # Check each obstacle line
  for line in agent.world.getLines():

    # If any line is too close to the agent, then we can't jump to this position
    if minimumDistance(line, position) < (AGENT_WIDTH/2):
      return False

  return True

def drawDodgePositions(agent, positions):
  crosses = []
  for position in positions:
    crosses.append(position)
  agent.world.crosses = crosses

## AOE Stuff
def enemeyInAOERadius(agent):
  visbleBullets = agent.getVisibleType(Minion)
  visbleBullets.extend(agent.getVisibleType(Hero))

  for enemy in visbleBullets:
    if enemy.getTeam() != agent.getTeam() and distance(agent.getLocation(), enemy.getLocation()) < (AREAEFFECTRANGE*agent.getRadius()):
      return True

  return False

def shouldFireAOE(agent):
  return agent.canareaeffect and enemeyInAOERadius(agent)

def handleAOEFire(agent):
  if shouldFireAOE(agent):
    agent.areaEffect()
    return True

  return False

def shootWhileRunning(agent):
  visbleAgents = agent.getVisibleType(Minion)
  visbleAgents.extend(agent.getVisibleType(Hero))

  target = None
  for visbleAgent in visbleAgents:
    if visbleAgent.getTeam() != agent.getTeam() and distance(agent.getLocation(), visbleAgent.getLocation()) < BIGBULLETRANGE - 2:
      target = visbleAgent
      break

  if target is not None:
    if distance(agent.getLocation(), target.getLocation()) <= AREAEFFECTRANGE + target.getRadius():
      agent.areaEffect()
    else:
      leadShootTarget(agent, target)
  return

def leadShootTarget(agent, target):
  # Target not moving
  if target.moveTarget == None:
    shootTarget = target.getLocation()

  # Target moving
  else:
    offset = getTargetOffset(target.getLocation(), target.moveTarget, agent.getLocation())
    shootTarget = (target.getLocation()[0]+offset[0], target.getLocation()[1]+offset[1])

  agent.turnToFace(shootTarget)
  agent.shoot()

def getTargetOffset(target, moveTarget, playerPos):
  # Calculate lead factor
  distanceToTarget = distance(playerPos, moveTarget)
  timeToTarget = distanceToTarget/BIGBULLETSPEED[0]
  leadFactor = timeToTarget*SPEED[0]

  # Create vector from start/end and normalize
  vector = (moveTarget[0]-target[0],moveTarget[1]-target[1])
  normalizedDirection = normalize(vector)

  # Calculate offset
  offset = (normalizedDirection[0]*leadFactor,normalizedDirection[1]*leadFactor)

  return offset

def normalize(vector):
  # theta = getAngleVector(vector)
  # rad = math.radians(theta)
  # normalizedDirection = (math.cos(rad), -math.sin(rad))

  vectorMag = getVectorMag(vector)
  normalizedDirection = (vector[0]/vectorMag, vector[1]/vectorMag)

  return normalizedDirection

def getAngleVector(vector):
  theta = math.atan(vector[1]/vector[0])
  if theta < 0:
    theta = theta + 360.0
  return theta

def getVectorMag(vector):
  return math.sqrt((vector[0]*vector[0])+(vector[1]*vector[1]))

TREE = [(Selector, 'Sel1'), [(HitpointDaemon, 0.5, 'HealthCheck'), [(Selector, 'Sel2'), [(BuffDaemon, 2, 'BuffCheck'), [(Sequence, 'Seq1'), (Chase, 'Hero', 'ChaseHero'), (Kill, 'Hero', 'KillHero')]], [(Sequence, 'Seq2'), (Chase, 'Minion', 'ChaseMinion'), (Kill, 'Minion', 'KillMinion')]]], (Retreat, 0.5, 'Retreat')]
