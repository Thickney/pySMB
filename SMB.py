import pygame
import sys
from pygame.locals import *

####################################
# Constants
####################################

# Game
worldTime = 500

# General Colours
red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
lightBlue = [135,206,250]
white = [255,255,255]
black = [0,0,0]
grey = [150,150,150]
gold = [255,215,0]
groundBrown = [160,82,45]
brickBrown = [205,133,63]

# Entity Colours
koopaColor = [50, 205, 50]
goombaColor = [220, 110, 75]
marioColor = white
mushroomColor = red
starColor = gold
coinColor = gold
oneUpColor = [40, 230, 40]
flowerColor = [200, 50, 10]

# Tiles
tileWidth = 50
blankTile = ' '
groundTile = 'g'
marioTile = 'm'
goombaTile = '@'
koopaTile = '#'
pipeTile = 'p'
blockTile = 'b'
bCoinTile = '+'
qCoinTile = '-'
qMushTile = '1'
qOneUpTile = '2'
qStarTile = '*'

# Physics
gravity = 0.02
maxVelocity = 1
marioWalk = 0.5
marioRun = 1.0

####################################
# Classes
####################################

# Camera
class Camera:
    def __init__ (self):
        self.x = 0
        self.y = 0
        self.w = screenSize[0]
        self.h = screenSize[1]
        self.getValues()

    def reset (self):
        self.x = 0
        self.y = 0

    def update (self):
        self.getValues()

    def getValues (self):
        mario = level.getMario()
        if mario is None:
            return
        if mario.x > self.x + self.w/2 - mario.w/2:
            self.x = level.getMario().x - screenSize[0]/2 + tileWidth/2

        # Make sure mario doesn't move off-screen to the left
        if mario.x < self.x:
            mario.x = self.x

# Hud
class HUD (object):
    def __init__ (self):
        self.reset()
        self.world = "1-1"
        self.scoreX = screenSize[0] / 8
        self.worldX = screenSize[0] - screenSize[0] / 2
        self.coinsX = screenSize[0] / 4 + screenSize[0] / 8
        self.timeX = screenSize[0] - screenSize[0] / 4
        self.y = 50
        self.marioString = "MARIO"
        self.worldString = "WORLD"
        self.timeString = "TIME"

    def reset (self):
        self.score = 0
        self.coins = 0
        self.elapsed = 0
        self.timeRemaining = worldTime

    def update (self, deltaTime):
        self.elapsed += deltaTime

        if self.elapsed > 1000:
            self.timeRemaining -= 1
            
            remainder = self.elapsed - 1000
            self.elapsed = remainder

        if self.timeRemaining == 0:
            level.getMario().removeLife()
            level.reset()
            camera.reset()
            self.reset()
            
    def draw (self):
        # Score
        ren = font.render(self.marioString, False, white)
        screen.blit(ren, (self.scoreX, self.y - 25))
        scoreString = "%08d"%self.score
        ren = font.render(scoreString, False, white)
        screen.blit(ren, (self.scoreX, self.y))

        # Coins
        coinString = "O x %02d"%self.coins
        ren = font.render(coinString, False, white)
        screen.blit(ren, (self.coinsX, self.y))

        # World
        ren = font.render(self.worldString, False, white)
        screen.blit(ren, (self.worldX, self.y - 25))
        ren = font.render(self.world, False, white)
        screen.blit(ren, (self.worldX, self.y))

        # Time
        ren = font.render(self.timeString, False, white)
        screen.blit(ren, (self.timeX, self.y - 25))
        ren = font.render(str(self.timeRemaining), False, white)
        screen.blit(ren, (self.timeX, self.y))

# Struct
class Struct (object):
    def __init__ (self, **entries):
        self.__dict__.update(entries)

# Entity
class Entity (object):
    x = 0
    y = 0
    w = 0
    h = 0
    rect = Rect(x,y,w,h)
    color = [0,0,0]
    direction = "right"
    currState = None
    prevState = None
        
    def __init__ (self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.rect = Rect(x,y,w,h)
        self.allStates = {}
        self.collidingObjects = []
        self.hasCollision = False

    def left (self):
        return self.x
    def right (self):
        return self.x + self.w
    def bottom (self):
        return self.y + self.h
    def top (self):
        return self.y
    def setY (self, y):
        self.y = y
        self.rect = Rect(self.x, self.y, self.w, self.h)
    def setX (self, x):
        self.x = x
        self.rect = Rect(self.x, self.y, self.w, self.h)

    def translate (self, dx, dy):
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

        self.x += dx

        if isinstance(self, Mario) and self.x < 0:
            self.x = 0
        
        self.y += dy
        self.rect = Rect(self.x,self.y,self.w,self.h)

    def changeState (self, stateID):
        if self.allStates.get(stateID) is None:
            return
        else:
            self.newState = self.allStates.get(stateID)
            self.currState.exitState(self)
            self.prevState = self.currState
            self.currState = self.newState
            self.currState.enterState(self)

    def addCollision (self, collided):
        self.collidingObjects.append(collided)
        self.hasCollision = True

    def draw (self):
        pygame.draw.rect(screen, self.color, [self.x - camera.x, self.y - camera.y, self.w, self.h], 0)

# Enemy
class Enemy (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)

# Coin
class Coin (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":CoinStateIdle(), "unused":CoinStateUnused() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.active = False

    def update (self, deltaTime):
        if self.active:
            self.currState.execute(self, deltaTime)

    def draw (self):
        if self.active:
            Entity.draw(self)    

# BrickBlock
class BrickBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":BrickBlockStateIdle(), "hitLight":BrickBlockStateHitLight(), "hitHard":BrickBlockStateHitHard(), "coinHit":BrickBlockStateCoinHit() }   
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.destroyed = False
        self.hasCoins = False
        self.used = False
        self.numCoins = 8
        
    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

    def draw (self):
        if not self.destroyed:
            Entity.draw(self)

# QuestionBlock
class QuestionBlock (Entity):
    def __init__ (self, x, y, w, h, contents, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":QuestionBlockStateIdle(), "hit":QuestionBlockStateHit() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.contents = contents
        self.used = False

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# OneUpBlock
class OneUpBlock (Entity):
    def __init__ (self, x, y, w, h, contents, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":OneUpBlockStateIdle(), "hit":QuestionBlockStateHit() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.contents = contents
        self.used = False
        self.found = False

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

    def draw (self):
        if self.found:
            Entity.draw(self)

# GroundBlock 
class GroundBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":GroundBlockStateIdle() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# Mushroom
class Mushroom (Entity):
    def __init__ (self, x, y, w, h, mType, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "spawn":MushroomStateSpawn(), "move":MushroomStateMove(), "fall":MushroomStateFall() }
        self.prevState = self.allStates.get("spawn")
        self.currState = self.prevState
        self.active = False
        self.dy = 0
        self.velocity = 0
        self.mType = mType

    def update (self, deltaTime):
        if self.active:
            self.currState.execute(self, deltaTime)

    def draw (self):
        if self.active:
            Entity.draw(self)

# Goomba
class Goomba (Enemy):
    def __init__ (self, x, y, w, h, spawnX, color):
        Enemy.__init__(self, x, y, w, h, color)
        self.allStates = { "wait":EnemyStateWait(), "move":EnemyStateMove(), "fall":EnemyStateFall(), "stomped":GoombaStateStomped(), "hit":EnemyStateHit() }
        self.prevState = self.allStates.get("wait")
        self.currState = self.prevState
        self.spawnX = spawnX
        self.direction = "left"
        self.isSpawned = False
        self.isDead = False
        self.isDeadDead = False #lulz
        self.velocity = 0
        self.dy = 0

    def update (self, deltaTime):
        if not self.isDeadDead:
            self.currState.execute(self, deltaTime)

    def draw (self):
        if self.isSpawned and not self.isDeadDead:
            Entity.draw(self)

# Koopa
class Koopa (Enemy):
    def __init__ (self, x, y, w, h, spawnX, color):
        Enemy.__init__(self, x, y, w, h, color)
        self.allStates = { "wait":EnemyStateWait(), "move":EnemyStateMove(), "fall":EnemyStateFall(), "stomped":KoopaStateStomped(), "shellMove":KoopaStateShellMove(), "hit":EnemyStateHit() }
        self.prevState = self.allStates.get("wait")
        self.currState = self.prevState
        self.spawnX = spawnX
        self.direction = "left"
        self.isSpawned = False
        self.isDead = False
        self.isDeadDead = False 
        self.velocity = 0
        self.dy = 0
        self.inShell = False

    def update (self, deltaTime):
        if not self.isDeadDead:
            self.currState.execute(self, deltaTime)

    def draw (self):
        if self.isSpawned and not self.isDeadDead:
            Entity.draw(self)

# Pipe
class Pipe (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":PipeStateIdle() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# Mario
class Mario (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":MarioStateIdle(), "move":MarioStateMove(), "jump":MarioStateJump(), "fall":MarioStateFall() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.speed = 0.5
        self.isDead = False
        self.dy = 0
        self.velocity = 0
        self.lives = 3
        self.startX = x
        self.startY = y
        self.isSuper = False
        self.isCrouch = False

    def addLife (self):
        self.lives += 1

    def removeLife (self):
        self.lives -= 1
        if self.lives < 0:
            self.isDead = True

    def reset (self):
        self.setX(self.startX)
        self.setY(self.startY)

    def tryCrouch (self):
        if not self.isSuper or self.isCrouch:
            return

        # Resize and set crouch = True
        self.y += self.h/2
        self.h /= 2
        self.rect = Rect(self.x, self.y, self.w, self.h)
        self.isCrouch = True

    def tryUnCrouch (self):
        if not self.isSuper or not self.isCrouch:
            return

        # Resize and set crouch = False
        self.y -= self.h
        self.h *= 2
        self.rect = Rect(self.x, self.y, self.w, self.h)
        self.isCrouch = False
        
    def getSuper (self):
        return self.isSuper

    def setSuper (self, isSuper):
        if isSuper and self.isSuper:
            return
        if not isSuper and not self.isSuper:
            return
        
        if isSuper and not self.isSuper and not self.isCrouch:
            self.y -= self.h
            self.h *= 2
            self.rect = Rect(self.x, self.y, self.w, self.h)

        elif not isSuper and self.isSuper and not self.isCrouch:
            self.y += self.h/2
            self.h /= 2
            self.rect = Rect(self.x, self.y, self.w, self.h)
        
        self.isSuper = isSuper
        
    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)


# State
class State (object):

    def enterState (self, entity):
        raise NotImplementedError("Please Implement enter() in State subclass.")

    def execute (self, entity, deltaTime):
        raise NotImplementedError("Please Implement execute() in State subclass.")

    def exitState (self, entity):
        raise NotImplementedError("Please Implement exit() in State subclass.")

# MarioStateIdle
class MarioStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            entity.changeState("jump")
        elif key[K_a]:
            entity.direction = "left"
            entity.changeState("move")
        elif key[K_d]:
            entity.direction = "right"
            entity.changeState("move")
        elif key[K_s]:
            entity.tryCrouch()
        elif not key[K_s]:
            entity.tryUnCrouch()

        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity.rect, tile.rect)
                if isinstance(tile, Enemy) and not tile.isDead and (sides.left or sides.right or sides.top):
                    entity.removeLife()
            resetCollisions(entity)

    def exitState (self, entity):
        resetCollisions(entity)

# MarioStateMove
class MarioStateMove (State):
    def enterState (self, entity):
        self.run = False
    
    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()

        # Check for move off of any platform
        shouldFall = should_fall(entity)
        
        if shouldFall:
            entity.changeState("fall")

        if key[K_SPACE]:
            entity.changeState("jump")
        
        if key[K_LSHIFT]:
            self.run = True
            
        if key[K_a]:
            if self.run:
                entity.translate(-(entity.speed) * 2 * deltaTime, 0)
            else:
                entity.translate(-(entity.speed) * deltaTime, 0)
            entity.direction = "left"
            
        if key[K_d]:
            if self.run:
                entity.translate(entity.speed * 2 * deltaTime, 0)
            else:
                entity.translate(entity.speed * deltaTime, 0)
            entity.direction = "right"

        if key[K_s]:
            entity.tryCrouch()

        if not key[K_s]:
            entity.tryUnCrouch()

        if not key[K_LSHIFT]:
            self.run = False

        if not key[K_a] and not key[K_d]:
            entity.changeState("idle")

        # Check for move into something.
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                if isinstance(tile.currState, EnemyStateHit):
                    continue
                
                sides = collision_sides(entity.rect, tile.rect)
                if isinstance(tile, Enemy) and (sides.left or sides.right or sides.top):
                    # If an enemy and still alive then hurt mario.
                    if not tile.isDead:
                        entity.removeLife()
                if sides.left:
                    entity.setX(tile.x + tile.w)
                elif sides.right:
                    entity.setX(tile.x - entity.w)
            resetCollisions(entity)
 
    def exitState (self, entity):
        resetCollisions(entity)

# MarioStateJump
class MarioStateJump (State):
    def enterState (self, entity):
        entity.dy = 0
        entity.velocity = -0.2
        self.startHeight = entity.y
        self.dx = 0

    def execute (self, entity, deltaTime):
        # Check in-air movement.
        key = pygame.key.get_pressed()
        speed = entity.speed
        jumpGravity = gravity

        if key[K_LSHIFT]:
            speed *= 2
            jumpGravity *= 0.9
        if key[K_a]:
            entity.direction = "left"
            self.dx = -speed
        if key[K_d]:
            entity.direction = "right"
            self.dx = speed

        # Check collisions.
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                if isinstance(tile.currState, EnemyStateHit):
                    continue
                
                sides = collision_sides(entity.rect, tile.rect)
                if sides.top and not isinstance(tile, Pipe) and not isinstance(tile, GroundBlock):
                    entity.setY(tile.bottom() + (entity.y - tile.y))
                    entity.velocity = 0
                    entity.dy = 0
                if sides.bottom:
                    entity.dy = 0
                    if isinstance(tile, Enemy) and not tile.isDead:
                        entity.velocity = -0.15
                    else:
                        entity.setY(tile.top() - entity.h)
                        entity.changeState("idle")
                        return

        # Don't go so fast that collisions are missed
        if entity.dy > maxVelocity:
            entity.dy = maxVelocity
        else:
            entity.dy += entity.velocity
        
        entity.velocity += jumpGravity
        entity.translate(self.dx * deltaTime, entity.dy * deltaTime)

    def exitState (self, entity):
        resetCollisions(entity)
    

# MarioStateFall
class MarioStateFall (State):
    def enterState (self, entity):
        self.dx = 0
        entity.velocity = 0
    
    def execute (self, entity, deltaTime):
        # Check in-air movement.
        key = pygame.key.get_pressed()
        speed = entity.speed

        if key[K_LSHIFT]:
            speed *= 2
        if key[K_a]:
            entity.direction = "left"
            self.dx = -speed
        if key[K_d]:
            entity.direction = "right"
            self.dx = speed

        # Check for landing
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                if isinstance(tile.currState, EnemyStateHit):
                    continue
                
                sides = collision_sides(entity.rect, tile.rect)
                if sides.bottom:
                    if isinstance(tile, Enemy) and not tile.isDead:
                        entity.dy = 0
                        entity.velocity = -0.15
                    else:
                        entity.setY(tile.top() - entity.h)
                        entity.changeState("idle")
                        return
        
        if entity.dy > maxVelocity:
            entity.dy = maxVelocity
        else:
            entity.dy += entity.velocity
            
        entity.velocity += gravity
        entity.translate(self.dx * deltaTime, entity.dy * deltaTime)

    def exitState (self, entity):
        resetCollisions(entity)

# EnemyStateWait
class EnemyStateWait (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        # Wait until player reaches some X position on the
        # level before updating and drawing this enemy instance.
        if level.getMario().x > entity.spawnX:
            entity.changeState("move")

    def exitState(self, entity):
        entity.isSpawned = True

# EnemyStateMove
class EnemyStateMove (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.direction == "left":
            entity.translate(-(0.1 * deltaTime), 0)
        else:
            entity.translate(0.1 * deltaTime, 0)

        # Check if should fall.
        shouldFall = should_fall(entity)
        if shouldFall:
            entity.changeState("fall")

        # Check for move into something.
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity.rect, tile.rect)
                
                # That something was Mario.
                if sides.top and isinstance(tile, Mario):
                    entity.changeState("stomped")
                    
                if sides.left:
                    entity.setX(tile.x + tile.w)
                    entity.direction = "right"
                elif sides.right:
                    entity.setX(tile.x - entity.w)
                    entity.direction = "left"
            resetCollisions(entity)

    def exitState(self, entity):
        return

# EnemyStateFall
class EnemyStateFall (State):
    def enterState (self, entity):
        entity.velocity = 0

    def execute (self, entity, deltaTime):
        # Update X
        if entity.direction == "left":
            entity.translate(-(0.1 * deltaTime), 0)
        else:
            entity.translate(0.1 * deltaTime, 0)

        # Update Y
        landed = updateFall(entity, deltaTime)

        # Check land
        if landed:
            entity.changeState("move")

    def exitState(self, entity):
        return

# EnemyStateHit
class EnemyStateHit (State):
    def enterState (self, entity):
        entity.isDead = True
        self.dy = -4.0

    def execute (self, entity, deltaTime):
        entity.translate(0, self.dy)
        self.dy += gravity * deltaTime
        if entity.y > camera.h:
            entity.isDeadDead = True
            level.removeEntity(entity)

    def exitState (self, entity):
        return

# GoombaStateStomped
class GoombaStateStomped (State):
    def enterState (self, entity):
        self.time = 0
        self.squishTime = 1000 # one second
        entity.y += entity.h/2
        entity.h /= 2
        entity.rect = Rect(entity.x, entity.y, entity.w, entity.h)
        entity.isDead = True

    def execute (self, entity, deltaTime):
        self.time += deltaTime

        # When time is up, switch to any state to remove goomba for good.
        if self.time > self.squishTime:
            entity.changeState("move")

    def exitState(self, entity):
        entity.isDeadDead = True
        level.removeEntity(entity)

# KoopaStateStomped
class KoopaStateStomped (State):
    def enterState (self, entity):
        self.time = 0
        self.recoverTime = 5000 # five seconds
        if entity.inShell == False:
            entity.y += entity.h/2
            entity.h /= 2
            entity.rect = Rect(entity.x, entity.y, entity.w, entity.h)
        entity.inShell = True
        entity.isDead = True

    def execute (self, entity, deltaTime):
        self.time += deltaTime

        # Come back out of shell.
        if self.time > self.recoverTime:
            entity.isDead = False
            entity.inShell = False
            entity.changeState("move")
            entity.y -= entity.h*2
            entity.h *= 2
            entity.rect = Rect(entity.x, entity.y, entity.w, entity.h)
            return

        # Otherwise check for mario hitting it in some direction.
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity.rect, tile.rect)
                if isinstance(tile, Mario):
                    # Decide which way to shoot shell.
                    if tile.x <= entity.x:
                        entity.direction = "right"
                    else:
                        entity.direction = "left"
                    # Shoot shell.
                    entity.isDead = False
                    entity.changeState("shellMove")
            resetCollisions(entity)

    def exitState (self, entity):
        return

# KoopaStateShellMove
class KoopaStateShellMove (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.direction == "left":
            entity.translate(-(marioRun * deltaTime), 0)
        else:
            entity.translate(marioRun * deltaTime, 0)

        # Check if should fall.
        shouldFall = should_fall(entity)
        if shouldFall:
            entity.changeState("fall")

        # Check for move into something.
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity.rect, tile.rect)

                if isinstance(tile, Enemy):
                    tile.changeState("hit")
                
                elif sides.top and isinstance(tile, Mario):
                    entity.changeState("stomped")
                
                elif sides.left:
                    entity.setX(tile.x + tile.w)
                    entity.direction = "right"
                    
                elif sides.right:
                    entity.setX(tile.x - entity.w)
                    entity.direction = "left"
            resetCollisions(entity)

    def exitState(self, entity):
        return

# QuestionBlockStateIdle
class QuestionBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                # If Mario jumped up and collided with block.
                if isinstance(tile, Mario) and tile.y > entity.y:
                    entity.changeState("hit")
            resetCollisions(entity)

    def exitState(self, entity):
        return

# OneUpBlockStateIdle
class OneUpBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity.rect, tile.rect)
                if sides.bottom and isinstance(tile, Mario) and tile.y > entity.y:
                    entity.changeState("hit")
                    entity.found = True
            resetCollisions(entity)

    def exitState(self, entity):
        return

# QuestionBlockStateHit
class QuestionBlockStateHit (State):
    def enterState (self, entity):
        entity.color = grey
        if not entity.used:
            entity.used = True
            if entity.contents == "coin":
                for obj in level.entities:
                    if isinstance(obj, Coin):
                        obj.setX(entity.x + 20)
                        obj.setY(entity.y - tileWidth)
                        obj.changeState("idle")

            elif entity.contents == "mushroom":
                for obj in level.entities:
                    if isinstance(obj, Mushroom) and obj.mType == "super":
                        obj.setX(entity.x)
                        obj.setY(entity.y)
                        obj.changeState("spawn")

            elif entity.contents == "1up":
                for obj in level.entities:
                    if isinstance(obj, Mushroom) and obj.mType == "1up":
                        obj.setX(entity.x)
                        obj.setY(entity.y)
                        obj.changeState("spawn")
                    
    def execute (self, entity, deltaTime):
        return

    def exitState (self, entity):
        return

# BrickBlockStateIdle
class BrickBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity.rect, tile.rect)
                # If Mario jumped up and collided with block.
                if isinstance(tile, Mario) and tile.y > entity.y and entity.hasCoins:
                    entity.changeState("coinHit")
                elif isinstance(tile, Mario) and tile.y > entity.y and not tile.isSuper:
                    entity.changeState("hitLight")
                elif isinstance(tile, Mario) and tile.y > entity.y and tile.isSuper:
                    entity.changeState("hitHard")
            resetCollisions(entity)

    def exitState(self, entity):
        return

# BrickBlockStateCoinHit
class BrickBlockStateCoinHit (State):
    def enterState (self, entity):
        self.tookCoin = False
        self.startY = entity.y
        self.maxY = entity.y - entity.h/2
        self.step = -0.2

    def execute (self, entity, deltaTime):
        if not entity.used and entity.hasCoins:
            if not self.tookCoin:
                # Spawn coin
                for obj in level.entities:
                    if isinstance(obj, Coin):
                        obj.setX(entity.x + 20)
                        obj.setY(entity.y - tileWidth)
                        obj.changeState("idle")
                    
                # Update coins left in block
                entity.numCoins -= 1
                self.tookCoin = True
                if entity.numCoins == 0:
                    entity.hasCoins = False
                    entity.used = True
                    entity.color = grey

            # Nudge block up then back down
            entity.setY(entity.y + self.step * deltaTime)
            if entity.y <= self.maxY:
                self.step *= -1
            if entity.y >= self.startY:
                entity.setY(self.startY)
                entity.changeState("idle")

    def exitState(self, entity):
        return

# BrickBlockStateHitLight
class BrickBlockStateHitLight:
    def enterState (self, entity):
        self.done = False
        self.startY = entity.y
        self.maxY = entity.y - entity.h/2
        self.step = -0.2

    def execute (self, entity, deltaTime):
        entity.setY(entity.y + self.step * deltaTime)
        if entity.y <= self.maxY:
            self.step *= -1
        if entity.y >= self.startY:
            entity.setY(self.startY)
            entity.changeState("idle")

    def exitState(self, entity):
        return

# BrickBlockStateHitHard
class BrickBlockStateHitHard:
    def enterState (self, entity):
        # Tile is destroyed, don't draw and only update bits now
        entity.destroyed = True

        # Initialize block bits
        self.topStep = -0.4
        self.bottomStep = -0.2
        self.tinySize = entity.w/2
        self.tiny = [None, None, None, None]
        self.tiny[0] = Rect(entity.x, entity.y, self.tinySize, self.tinySize) #tl
        self.tiny[1] = Rect(entity.x + self.tinySize, entity.y, self.tinySize, self.tinySize) #tr
        self.tiny[2] = Rect(entity.x, entity.y + self.tinySize, self.tinySize, self.tinySize) #bl
        self.tiny[3] = Rect(entity.x + self.tinySize, entity.y + self.tinySize, self.tinySize, self.tinySize) #br

    def execute (self, entity, deltaTime):
        numOffScreen = 0
        # Top-left
        self.tiny[0].x -= 0.05 * deltaTime
        self.tiny[0].y += self.topStep * deltaTime
        # Top-Right
        self.tiny[1].x += 0.05 * deltaTime
        self.tiny[1].y += self.topStep * deltaTime
        # Bottom-Left
        self.tiny[2].x -= 0.05 * deltaTime
        self.tiny[2].y += self.bottomStep * deltaTime
        # Bottom-Right
        self.tiny[3].x += 0.05 * deltaTime
        self.tiny[3].y += self.bottomStep * deltaTime

        self.topStep += gravity
        self.bottomStep += gravity
            
        # Check if done
        y1 = self.tiny[0].y
        y2 = self.tiny[1].y
        y3 = self.tiny[2].y
        y4 = self.tiny[3].y
        height = camera.h

        if y1 > height and y2 > height and y3 > height and y4 > height:
            level.removeTile(entity)

    def draw (self):
        for piece in self.tiny:
            pygame.draw.rect(screen, brickBrown, [piece.x - camera.x, piece.y - camera.y, self.tinySize, self.tinySize], 0)
        
    def exitState(self, entity):
        return

# GroundBlockStateIdle
class GroundBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return
        
    def exitState(self, entity):
        return

# PipeStateIdle
class PipeStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.hasCollision:
            resetCollisions(entity)
        
    def exitState(self, entity):
        return

# CoinStateIdle
class CoinStateIdle (State):
    def enterState (self, entity):
        entity.active = True
        self.timer = 0
        self.delay = 1000
        hud.coins += 1

    def execute (self, entity, deltaTime):
        self.timer += deltaTime

        if self.timer > self.delay:
            entity.changeState("unused")

    def exitState(self, entity):
        return

# CoinStateUnused
class CoinStateUnused (State):
    def enterState (self, entity):
       entity.setX(-100)
       entity.setY(0)
       entity.active = False

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

# MushroomStateSpawn
class MushroomStateSpawn (State):
    def enterState (self, entity):
       entity.active = True
       self.startY = entity.y

    def execute (self, entity, deltaTime):
        dy = 0.05 * deltaTime
        entity.translate(0, -dy)
        if entity.y <= self.startY - tileWidth:
            entity.direction = "right"
            entity.changeState("move")

    def exitState(self, entity):
        return

# MushroomStateMove
class MushroomStateMove (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        if entity.direction == "left":
            entity.translate(-(0.15 * deltaTime), 0)
        else:
            entity.translate(0.15 * deltaTime, 0)

        # Check if should fall.
        shouldFall = should_fall(entity)
        if shouldFall:
            entity.changeState("fall")

        # Check for move into something.
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                if isinstance(tile, Coin) or isinstance(tile, Enemy):
                    return
                
                sides = collision_sides(entity.rect, tile.rect)

                checkMushroomMarioCollision(entity, tile)
                
                if sides.left:
                    entity.setX(tile.x + tile.w)
                    entity.direction = "right"
                    
                elif sides.right:
                    entity.setX(tile.x - entity.w)
                    entity.direction = "left"
            resetCollisions(entity)

    def exitState(self, entity):
        return

# MushroomStateFall
class MushroomStateFall (State):
    def enterState (self, entity):
        entity.velocity = 0

    def execute (self, entity, deltaTime):
        # Update X
        if entity.direction == "left":
            entity.translate(-(0.15 * deltaTime), 0)
        else:
            entity.translate(0.15 * deltaTime, 0)

        # Update Y
        landed = updateFall(entity, deltaTime)

        # Check land
        if landed:
            entity.changeState("move")

        # Check mario pick-up in air
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                if isinstance(tile, Coin) or isinstance(tile, Enemy):
                    return
                
                checkMushroomMarioCollision(entity, tile)

    def exitState(self, entity):
        return

####################################
# Levels
####################################

# Level
class Level:
    
    def __init__ (self, fileHandle):
        self.currentFileHandle = fileHandle
        self.reset()

    def reset (self):
        self.f = open(self.currentFileHandle)
        self.tileRows = self.f.readlines()
        self.map = []
        self.entities = []
        i = 0
        for row in self.tileRows:
            j = 0
            for tile in row:
                self.loadItem(tile, j, i)
                j += 1
            i += 1

        # Add reusable items.
        self.entities.append(Coin(-100, 0, 10, 30, coinColor))
        self.entities.append(Mushroom(-100, 100, tileWidth, tileWidth, "super", mushroomColor))
        #self.entities.append(Star(-100, 200, tileWidth, tileWidth, starColor))
        self.entities.append(Mushroom(-100, 300, tileWidth, tileWidth, "1up", oneUpColor))
        #self.entities.append(Flower(-100, 400, tileWidth, tileWidth, flowerColor))

    def loadItem (self, tile, x, y):
        xPos = x * tileWidth
        yPos = y * tileWidth

        if (tile == blankTile):
            return
        
        elif (tile == groundTile):
            self.map.append(GroundBlock(xPos, yPos, tileWidth, tileWidth, groundBrown))

        elif (tile == marioTile):
            self.entities.append(Mario(xPos, yPos+10, tileWidth-10, tileWidth-10, white))

        elif (tile == blockTile):
            self.map.append(BrickBlock(xPos, yPos, tileWidth, tileWidth, brickBrown))

        elif (tile == bCoinTile):
            coinBlock = BrickBlock(xPos, yPos, tileWidth, tileWidth, brickBrown)
            coinBlock.hasCoins = True
            self.map.append(coinBlock)

        elif (tile == qCoinTile):
            self.map.append(QuestionBlock(xPos, yPos, tileWidth, tileWidth, "coin", gold))

        elif (tile == qMushTile):
            self.map.append(QuestionBlock(xPos, yPos, tileWidth, tileWidth, "mushroom", gold))

        elif (tile == qOneUpTile):
            self.map.append(OneUpBlock(xPos, yPos, tileWidth, tileWidth, "1up", grey))

        elif (tile == pipeTile):
            self.map.append(Pipe(xPos, yPos, tileWidth, tileWidth, green))

        elif (tile == goombaTile):
            self.entities.append(Goomba(xPos, yPos, tileWidth, tileWidth, xPos - screenSize[0]/2, goombaColor))

        elif (tile == koopaTile):
            self.entities.append(Koopa(xPos, yPos, tileWidth, tileWidth, xPos - screenSize[0]/2, koopaColor))

    def update (self, deltaTime):
        for tile in self.map:
            tile.update(deltaTime)
            
        for entity in self.entities:
            entity.update(deltaTime)
        
        self.checkCollisions()

    def checkCollisions (self):
        for entity in self.entities:

            # Check Entity/Entity collisions.
            for entity2 in self.entities:
                if entity != entity2 and entity.rect.colliderect(entity2.rect):
                    entity.addCollision(entity2)
                    
            # Check Entity/World collisions.
            for tile in self.map:
                if tile.rect.colliderect(entity.rect):
                    entity.addCollision(tile)
                    tile.addCollision(entity)

    def removeEntity (self, entity):
        self.entities.remove(entity)

    def removeTile (self, tile):
        self.map.remove(tile)

    def addEntity (self, entity):
        self.entities.append(entity)
                
    def getMario (self):
        for entity in self.entities:
            if isinstance(entity, Mario):
                return entity
        return None

    def draw (self):
        for tile in self.map:
            tile.draw()

            if isinstance(tile, BrickBlock) and tile.destroyed:
                tile.currState.draw()
            
        for entity in self.entities:
            entity.draw()

# 1-1
class LevelOneOne (Level):
    def __init__ (self, fileHandle):
        Level.__init__(self, fileHandle)

    def update (self, deltaTime):
        Level.update(self, deltaTime)
        return


####################################
# Globals
####################################

# Display
pygame.init()
screenSize = [1280,720]
screenBGColor = lightBlue

# Levels
levelHandle = "1-1.txt"
level = LevelOneOne(levelHandle)

# Font
font = pygame.font.SysFont('Courier New', 26)

# Game
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("SMB")
camera = Camera()
hud = HUD()
clock = pygame.time.Clock()
running = True


####################################
# Functions
####################################

def resetCollisions (entity):
    entity.collidingObjects = []
    entity.hasCollision = False

def collision_sides (a, b):
    sides = Struct(left=False, right=False, top=False, bottom=False)
    
    left = Rect(a.left, a.top + 1, 1, a.height - 2)
    right = Rect(a.right, a.top + 1, 1, a.height - 2)
    top = Rect(a.left + 1, a.top, a.w - 2, 1)
    bottom = Rect(a.left + 1, a.bottom, a.width - 2, 1)

    if left.colliderect(b):
        sides.left = True
    if right.colliderect(b):
        sides.right = True
    if top.colliderect(b):
        sides.top = True
    if bottom.colliderect(b):
        sides.bottom = True

    return sides

def checkMushroomMarioCollision (entity, tile):
    if isinstance(tile, Mario):
        if entity.mType == "super":
            tile.setSuper(True)
            
        elif entity.mType == "1up":
            tile.addLife()

        # Reset Mushroom entity
        entity.setX(-100)
        entity.setY(100)
        entity.changeState("spawn")
        entity.active = False

def should_fall (entity):
    for tile in level.map:
        sides = collision_sides(entity.rect, tile.rect)
        if sides.bottom:
            return False
    return True

def updateFall (entity, deltaTime):
    landed = False
    
    # Check for landing
    if entity.hasCollision:
        for tile in entity.collidingObjects:
            sides = collision_sides(entity.rect, tile.rect)
            if sides.bottom:
                # If entity fell on Mario then it's an enemy
                # and this should trigger death or power-down in Mario.
                if isinstance(tile, Mario):
                    return
                
                entity.setY(tile.top() - entity.h)
                entity.changeState("idle")
                entity.hasCollision = False
                entity.collidingObjects = []
                return True 
    
    if entity.dy > maxVelocity:
        entity.dy = maxVelocity
    else:
        entity.dy += entity.velocity
        
    entity.velocity += gravity
    entity.translate(0, entity.dy * deltaTime)

    return landed

def render ():
    screen.fill(screenBGColor)
    level.draw()
    hud.draw()
    pygame.display.flip()

def tick ():
    deltaTime = clock.tick(60)
    level.update(deltaTime)
    camera.update()
    hud.update(deltaTime)
    

####################################
# Main loop
####################################

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    tick()
    render()

    mario = level.getMario()
    if not mario is None and (mario.y > screenSize[1] or mario.isDead):
        mario.removeLife()
        
        if mario.lives < 0:
            print "Game Over"
            running = False

        else:
            mario.isDead = False
            mario.reset()
            camera = Camera()

pygame.quit()



















