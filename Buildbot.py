#!/usr/bin/python

import pygame, sys, os
import math
import astar
import itertools
import util
import constants
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

class Gun(pygame.sprite.Sprite):
    def __init(self, _kind):
        self.add(allspritesGroup)
        self.kind = _kind

class Bot(pygame.sprite.Sprite): #derived from pygame.sprite.Sprite
    def __init__(self, size, xCell, yCell):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.add(allspritesGroup)
        self.add(botsGroup)
        
        self.size = size #0-2
        self.direction = 0 #0-16 clockwise 0=up
        self.index = 0 #0-4 start, 5-16 loop, 17-18 stop
        self.speed = 0

        self.gun = [0] * 3
        self.gun[0] = Gun(1) #0=none 1=cannon 2=laser 3=torch 4=rockets
        self.gun[1] = 0
        self.gun[2] = 0
        self.gunDirection = 0
        
        self.imageList = [0] * 19
        self.loadAnim(0)
        
        self.rect = self.imageList[self.index].get_rect()
        self.xy = util.grid_to_world((xCell, yCell)) #world x y coordinates
        self.hitRect = pygame.Rect(self.xy[0] - 10, self.xy[1] - 10, 20, 20) #hitbox
        
        self.path = None #grid waypoints for pathfinding
        self.pathPos = 0
        self.jumpCell((xCell, yCell))
        self.currentCell = (xCell, yCell)
        self.nextCell = (xCell, yCell)
        self.destCell = (xCell, yCell)
        allspritesGroup.change_layer(self, self.currentCell[1] * 10)
        botsGroup.change_layer(self, self.currentCell[1] * 10)
        
    #jump to a given cell
    def jumpCell(self, (x, y)):
        self.xy = util.grid_to_world((x, y))
        
    #load animation for int direction d to imageList
    def loadAnim(self, _dir):
        for iLoop in range(19):
            self.imageList[iLoop] = load_image(os.path.join(str(self.size), str(_dir), str(iLoop + 1) + '.bmp'), -1)
            
    #set the path with dest=(x, y)
    def pathSet(self, (x, y)):
        self.destCell = (x, y)
        if self.currentCell in blocked:
            blocked.remove(self.currentCell)
        astar.findpath(self.currentCell, self.destCell, blocked)
        self.path = astar.path #POINTS STORED IN REVERSE ORDER
        self.pathPos = len(self.path) - 1
        self.nextCell = self.path[len(self.path) - 2]
        self.setDirection(util.point_direction(self.xy, util.grid_to_world(self.nextCell)))
        #print self.currentCell
        #print blocked
        
    #check if any path cells are blocked
    def pathBlocked(self):
        for i in self.path:
            if i in blocked:
                if i != self.currentCell:
                    print 'Path Blocked at ' + str(i)
                    return True
        return False
        
    #set the direction dir=0-16
    def setDirection(self, _dir):
        if _dir != self.direction:
            self.loadAnim(int(round(_dir) % 16))
            self.direction = _dir

    def update(self):
        self.currentCell = util.world_to_grid(self.xy)
        if self.currentCell != self.destCell:
            self.speed = 8 - (self.size)
            if self.currentCell == self.nextCell:
                #if self.pathBlocked():
                #    self.pathSet(self.destCell)
                #else:
                self.pathPos -= 1
                self.nextCell = self.path[self.pathPos - 1]
                self.setDirection(util.point_direction(self.xy, util.grid_to_world(self.nextCell)))
                    #print 'pathpos ' + str(self.pathPos)
                    #print 'current cell ' + str(self.currentCell)
                    #print 'next cell ' + str(self.nextCell)
                    #print 'new direction ' + str(self.direction)
                    #print ' '
        else: #we've reached the destination
            self.speed = 0
            self.index = 0
            if self in movingGroup:
                blocked.append(self.currentCell)
                self.remove(movingGroup)
        self.image = self.imageList[self.index]
        self.index = ((self.index + 1) % 17) + (5 * (self.index == 16))

        self.gunDirection = int(round(self.direction) % 16)

        self.xy = util.add2(self.xy, util.speedDir_xy(self.speed, self.direction)) #move xy
        self.rect.center = (self.xy[0], self.xy[1] - (12 + (6 * self.size))) #move rect to xy
        self.hitRect.center = self.xy #move hitbox to xy

        allspritesGroup.change_layer(self, self.currentCell[1] * 10)
        botsGroup.change_layer(self, self.currentCell[1] * 10)
        

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
                mouseRect = util.view_to_world(pygame.mouse.get_pos(), view)
                if event.button == 3: #right click
                    for i in selectedGroup.sprites(): #move bots
                        i.add(movingGroup)
                        i.pathSet(util.world_to_grid(mouseRect))
                    mouseRect = 0
                    mouseDrag = 0
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and mouseRect != 0: #left click
                    #dragging
                    if mouseDrag:
                        mouseDrag = False
                        if not shiftPressed:
                            selectedGroup.empty()
                        selectedList = pygame.Rect(util.add2(mouseRect, map(lambda x: min(0,x), util.sub2(pygame.mouse.get_pos(), util.world_to_view(mouseRect, view)))), #move top left if width/height are negative
                                                map(lambda x: abs(x), util.sub2(pygame.mouse.get_pos(), util.world_to_view(mouseRect, view)))).collidelistall([i.hitRect for i in botsGroup.sprites()])
                        selectedGroup.add([botsGroup.get_sprite(i) for i in selectedList])
                    else:
                        selectedList = pygame.Rect(mouseRect, (1,1)).collidelist([i.hitRect for i in botsGroup.sprites()]) #index of selected bot
                        if selectedList != -1: #we're clicking a bot
                            if not shiftPressed:
                                selectedGroup.empty()
                            selectedGroup.add(botsGroup.get_sprite(selectedList))
                        else:
                            selectedGroup.empty()
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

        #draw blocked cells
        for i in blocked:
            pygame.draw.circle(baseSurface, pygame.Color(255, 0, 0, 0), util.grid_to_world(i), 4, 4)

        #draw bot selections
        for i in selectedGroup:
            baseSurface.blit(pygame.transform.scale(pygame.transform.rotate(sprBotSelect, step * 2), (77, 38)), (i.rect.centerx - 38, i.rect.centery + (i.size * 10)))
            #pygame.draw.ellipse(viewSurface, pygame.Color(int(70 + (math.sin(step / 100) * 70)), 170, int(70 + (math.sin(step / 100) * 70)), 0), i.rect.inflate(-(120 - (8 * i.size)),-(100 - (4 * i.size))).move(0, 30), 0)
                
        #draw allsprites
        allspritesGroup.draw(baseSurface)

        #draw bot weapons
        for i in botsGroup:
            baseSurface.blit(gunList[i.gunDirection + ((i.gun[0] - 1) * 16)], (i.rect.centerx - 100, i.rect.centery - (60 + (5 * i.size)) + gunOffset[i.size][i.index]))
            #baseSurface.blit(sprBotGunMount, (i.rect.centerx - 6, i.rect.centery - (25 + (5 * i.size))))

        #draw grid
        for i in range(0, 1000, constants.cellSize):
            pygame.draw.line(baseSurface, pygame.Color(0,0,0,0), (0, i), (1000, i), 1)
            pygame.draw.line(baseSurface, pygame.Color(0,0,0,0), (i, 0), (i, 1000), 1)
            
        #draw mouse selection box
        if mouseDrag:
            pygame.draw.rect(baseSurface, pygame.Color(50, 170, 0, 0), pygame.Rect(mouseRect, util.sub2(pygame.mouse.get_pos(), util.world_to_view(mouseRect, view))), 2)
            
        #draw bot paths
        for i in movingGroup:
            pygame.draw.line(baseSurface, pygame.Color(50, 170, 0, 0), i.xy, util.grid_to_world(i.destCell), 2)
            if i.pathPos > 1:
                pygame.draw.lines(baseSurface, pygame.Color(200, 0, 0, 0), False, [util.grid_to_world(p) for p in i.path[:i.pathPos]], 2)
            
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

baseSurface = pygame.Surface((constants.room_w * constants.cellSize, constants.room_h * constants.cellSize))
baseSurface = baseSurface.convert()

#pathfinding
astar.max_x = constants.room_w
astar.max_y = constants.room_h
blocked = []

if pygame.font:
    font = pygame.font.Font(None, 36) #new font object
    text = font.render("m", 1, (10, 10, 10)) #returns the surface with text
    textpos = text.get_rect()
    textpos.centerx = baseSurface.get_rect().centerx
    baseSurface.blit(text, textpos)

#y-offsets for guns during walking animation
gunOffset = [[0, 0, 0, 3, 6, 4, 1, 0, 1, 4, 6, 4, 1, 0, 1, 4, 6, 4, 1],
            [0, 0, 0, 4, 8, 6, 2, 0, 2, 6, 8, 6, 2, 0, 2, 6, 8, 6, 2],
            [0, 0, 0, 6, 12, 9, 3, 0, 3, 9, 12, 9, 3, 0, 3, 9, 12, 9, 3]]

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

gunList = [0] * 64 #0-15=cannon 16-31=laser 32-47=torch 48-63=rockets
for t in range(4):
    for i in range(16):
        gunList[(t * 16) + i] = load_image(os.path.join('weapons', str(t), str(i) + '.bmp'), -1)
        gunList[(t * 16) + i].convert()

allspritesGroup = pygame.sprite.LayeredUpdates()
botsGroup = pygame.sprite.LayeredUpdates()
selectedGroup = pygame.sprite.Group()
movingGroup = pygame.sprite.Group()

bot = Bot(2, 15, 10)

bot1 = Bot(1, 15, 10)

bot2 = Bot(0, 15, 10)

view = View(0,0)

clock = pygame.time.Clock()
main()