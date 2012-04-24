#!/usr/bin/python

import pygame, sys, os
import math
import astar
import itertools
from pygame.locals import *

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname) #load a surface
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert() #convert pixel format
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL) #the transparent color
    return image

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound

#add
def parallel_add((x1,y1), (x2,y2)):
    return (x1 + x2, y1 + y2)
    #return map(lambda (x, y): x + y, zip((x1, y1), (x2, y2)))
    
#subtract
def parallel_sub((x1,y1), (x2,y2)):
    return (x1 - x2, y1 - y2)
    #return map(lambda (x, y): x - y, zip((x1, y1), (x2, y2)))
    
#convert view coordinates to world coordinates
def view_to_world((x,y)):
    return (x + view.x, y + view.y)
    #return parallel_add((x,y), (view.x,view.y))

#convert world coordinates to view coordinates
def world_to_view((x,y)):
    return (x - view.x, y - view.y)
    #return parallel_sub((x,y), (view.x,view.y))
    
#convert world coordinates to grid coordinates
def world_to_grid((x, y)):
    return (x // 10, y // 10)

#convert grid coordinates to world coordinates
def grid_to_world((x, y)):
    return (x * 10, y * 10)
    
#calculate x and y from given speed and direction
def speedDir_xy(s, d):
    return (math.sin(d * math.pi / 8) * s, -math.cos(d * math.pi / 8) * s)
    
#return rounded direction from 1 to 2
def point_direction((x1, y1), (x2, y2)):
    return int(round(math.atan2(x2 - x1, y1 - y2) / (math.pi / 8)) % 16)

class Fist(pygame.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('ship4.bmp', -1)
        self.punching = 0

    def update(self):
        "move the fist based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        "returns true if the fist collides with the target"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        "called to pull the fist back"
        self.punching = 0

class Chimp(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
    monkey when it is punched."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('ship4.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 9
        self.dizzy = 0

    def update(self):
        "walk or spin, depending on the monkeys state"
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        "move the monkey across the screen, and turn at the ends"
        newpos = self.rect.move((self.move, 0))
        if self.rect.left < self.area.left or \
            self.rect.right > self.area.right:
            self.move = -self.move
            newpos = self.rect.move((self.move, 0))
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.rect = newpos

    def _spin(self):
        "spin the monkey image"
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def punched(self):
        "this will cause the monkey to start spinning"
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image

class Bot(pygame.sprite.Sprite): #derived from pygame.sprite.Sprite
    def __init__(self, size, xCell, yCell):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.add(allspritesGroup)
        self.add(botsGroup)
        
        self.size = size #0-2
        self.direction = 0 #0-15 clockwise 0=up
        self.index = 0 #currently drawn image
        self.speed = 0
        
        self.imageList = [0] * 19
        self.loadAnim(0)
        
        self.rect = self.imageList[self.index].get_rect()
        
        self.path = None #grid waypoints for pathfinding
        self.pathPos = 0
        self.jumpCell((xCell, yCell))
        self.currentCell = (xCell, yCell)
        self.nextCell = (xCell, yCell)
        self.destCell = (xCell, yCell)
        
        self.pathSet((30, 40))
        print self.path
        
    #jump to a given cell
    def jumpCell(self, (x, y)):
        self.rect.center = grid_to_world((x, y))
        
    #load animation for dir to imageList
    def loadAnim(self, dir):
        for iLoop in range(19):
            self.imageList[iLoop] = load_image(os.path.join(str(self.size), str(dir), str(iLoop + 1) + '.bmp'), -1)
            
    #set the path with dest=(x, y)
    def pathSet(self, (x, y)):
        self.destCell = (x, y)
        astar.findpath(self.currentCell, self.destCell, blocked)
        self.path = astar.path #POINTS STORED IN REVERSE ORDER
        self.pathPos = len(self.path) - 1
        self.nextCell = self.path[len(self.path) - 2]
        self.setDirection(point_direction(self.currentCell, self.nextCell))
        
    #check if any path cells are blocked
    def pathBlocked(self):
        for i in self.path:
            if i in blocked:
                return True
        return False
        
    #set the direction
    def setDirection(self, dir):
        if dir != self.direction:
            self.loadAnim(dir)
            self.direction = dir

    def update(self):
        self.currentCell = world_to_grid(self.rect.center)
        if self.currentCell != self.destCell:
            self.speed = 4
            if self.currentCell == self.nextCell:
                if self.pathBlocked():
                    self.pathSet(self.destCell)
                else:
                    self.pathPos -= 1
                    self.nextCell = self.path[self.pathPos - 1]
                    self.setDirection(point_direction(self.currentCell, self.nextCell))
        else:
            self.speed = 0
        self.image = self.imageList[self.index]
        self.index = (self.index + 1) % 19
        self.rect.move_ip(speedDir_xy(self.speed, self.direction))
        

class View:
    def __init__(self, startX, startY):
        #top left corner of view
        self.x = startX
        self.y = startY
        
        self.xspd = 0
        self.yspd = 0
        
    def update(self):
        self.x = max(0, self.x + self.xspd)
        self.y = max(0, self.y + self.yspd)

def main():
    step = 0
    shiftPressed = False
    mouseDrag = False
    mouseRect = 0
    #scrolling with the mouse
    lScrolling = False
    rScrolling = False
    uScrolling = False
    dScrolling = False
    
    while True:
        clock.tick(30)
        step = (step + 1) % 1000
    # destroy objects 
    #for obj in allsprites:
        #if obj.timer == 0:
        #    obj = None
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                if mouseRect != 0:
                    mouseDrag = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_DOWN:
                    view.yspd += 10
                elif event.key == K_LEFT:
                        view.xspd -= 10
                elif event.key == K_UP:
                        view.yspd -= 10
                elif event.key == K_RIGHT:
                    view.xspd += 10
                elif event.key == K_LSHIFT:
                    shiftPressed = True
            elif event.type == KEYUP:
                if event.key == K_DOWN:
                    view.yspd -= 10
                elif event.key == K_LEFT:
                    view.xspd += 10
                elif event.key == K_UP:
                    view.yspd += 10
                elif event.key == K_RIGHT:
                    view.xspd -= 10
                elif event.key == K_LSHIFT:
                    shiftPressed = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1: #left click
                    mouseRect = view_to_world(pygame.mouse.get_pos())
                elif event.button == 3: #right click
                    selectedGroup.empty() #deselect all
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    #dragging
                    if mouseDrag:
                        mouseDrag = False
                        if not shiftPressed
                            selectedList.empty()
                        selectedList.add(pygame.Rect(parallel_add(mouseRect, map(lambda x: min(0,x), parallel_sub(pygame.mouse.get_pos(), world_to_view(mouseRect)))), #move top left if width/height are negative
                                                map(lambda x: abs(x), parallel_sub(pygame.mouse.get_pos(), world_to_view(mouseRect)))).collidelistall(botsGroup.sprites()))
                        for i in selectList:
                            botsGroup.get_sprite(i).selected = True
                        #if not shiftPressed:
                        #    for i in set(range(len(botsGroup.sprites()))).difference(set(selectList)):
                        #        botsGroup.get_sprite(i).selected = False
                    else:
                        selectList = pygame.Rect(mouseRect, (1,1)).collidelist(botsGroup.sprites())
                        if selectList != -1: #we're clicking a bot
                            if not shiftPressed:
                                for i in botsGroup.sprites():
                                    i.selected = False
                            botsGroup.get_sprite(selectList).selected = True
                        else:
                            
                    mouseRect = 0
            elif event.type == QUIT:
                return
                
        allspritesGroup.update()
        view.update()
                
        #screen scroll using mouse
        #left
        if pygame.mouse.get_pos()[0] < 30:
            if not lScrolling:
                view.xspd -= 10
                lScrolling = True
        elif lScrolling:
            view.xspd += 10
            lScrolling = False
            
        #right
        if pygame.mouse.get_pos()[0] > 610:
            if not rScrolling:
                view.xspd += 10
                rScrolling = True
        elif rScrolling:
            view.xspd -= 10
            rScrolling = False
            
        #up
        if pygame.mouse.get_pos()[1] < 30:
            if not uScrolling:
                view.yspd -= 10
                uScrolling = True
        elif uScrolling:
            view.yspd += 10
            uScrolling = False
            
        #down
        if pygame.mouse.get_pos()[1] > 450:
            if not dScrolling:
                view.yspd += 10
                dScrolling = True
        elif dScrolling:
            view.yspd -= 10
            dScrolling = False
        
        #draw floor tiles
        for w in range(view.x - (view.x % 80), view.x + 720, 80):
            for h in range(view.y - (view.y % 80), view.y + 560, 80):
                baseSurface.blit(sprFloor, (w, h))
                
        #draw bot selections
        for i in botsGroup:
            if i.selected:
                baseSurface.blit(pygame.transform.scale(pygame.transform.rotate(sprBotSelect, step * 2), (77, 38)), (i.rect.centerx - 38, i.rect.centery + (i.size * 10)))
                #pygame.draw.ellipse(viewSurface, pygame.Color(int(70 + (math.sin(step / 100) * 70)), 170, int(70 + (math.sin(step / 100) * 70)), 0), i.rect.inflate(-(120 - (8 * i.size)),-(100 - (4 * i.size))).move(0, 30), 0)
                
        #draw allsprites
        allspritesGroup.draw(baseSurface)
        
        #draw mouse selection box
        if mouseDrag:
            pygame.draw.rect(baseSurface, pygame.Color(50, 170, 0, 0), pygame.Rect(mouseRect, parallel_sub(pygame.mouse.get_pos(), world_to_view(mouseRect))), 2)
            
        #draw to view
        viewSurface.blit(baseSurface, (-view.x, -view.y))
        pygame.display.flip()

pygame.init()

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

window = pygame.display.set_mode((640,480)) #initialize window to display
pygame.display.set_caption('Buildbot')
viewSurface = pygame.display.get_surface() #the view surface

pygame.mouse.set_visible(1)

baseSurface = pygame.Surface((5000, 5000))
baseSurface = baseSurface.convert()

#pathfinding
astar.max_x = 500
astar.max_y = 500
blocked = []

if pygame.font:
    font = pygame.font.Font(None, 36) #new font object
    text = font.render("m", 1, (10, 10, 10)) #returns the surface with text
    textpos = text.get_rect()
    textpos.centerx = baseSurface.get_rect().centerx
    baseSurface.blit(text, textpos)

#whiff_sound = load_sound('whiff.wav')
#punch_sound = load_sound('punch.wav')

#load the bot animations
#imageList = [[[0] * 19] * 16] * 3
#for sLoop in range(3): #sizes
#	for dLoop in range(16): #directions
#		for iLoop in range(19): #images
#			imageList[sLoop][dLoop][iLoop] = load_image(os.path.join(str(sLoop), str(dLoop), str(iLoop + 1) + '.bmp'), -1)

sprBotSelect = load_image('bot_select.bmp')
sprBotSelect.convert()
sprBotSelect.set_colorkey(0, RLEACCEL)

sprFloor = load_image('floor_tile.bmp')
sprFloor.convert()

allspritesGroup = pygame.sprite.LayeredUpdates()
botsGroup = pygame.sprite.LayeredUpdates()
selectedGroup = pygame.sprite.Group()

bot = Bot(2, 5, 9)
bot._layer = 1

#bot2 = Bot(1, 10, 9)
#bot2._layer = 0

view = View(0,0)

clock = pygame.time.Clock()
main()