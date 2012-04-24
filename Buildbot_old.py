#!/usr/bin/python

import pygame, sys, os
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
    return image, image.get_rect()

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
  def __init__(self, size):
    pygame.sprite.Sprite.__init__(self) #call Sprite initializer
    self.size = size #0-2
    self.direction = 0 #0-15 clockwise 0=up
    self.index = 0 #currently drawn image
  def update(self):
    self.image, self.rect = imageList[self.size][self.direction][self.index]
    self.index = (self.index + 1) % 19

def main():
    while 1:
	clock.tick(30)
	for event in pygame.event.get():
	    if event.type == QUIT:
		return
	    elif event.type == KEYDOWN and event.key == K_ESCAPE:
		return
	    elif event.type == MOUSEBUTTONDOWN:
		if fist.punch(chimp):
		    punch_sound.play() #punch
		    chimp.punched()
		else:
		    whiff_sound.play() #miss
	    elif event.type == MOUSEBUTTONUP:
		fist.unpunch()
	allsprites.update()
	screen.blit(background, (0, 0))
	allsprites.draw(screen)
	pygame.display.flip()


pygame.init()

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

window = pygame.display.set_mode((640,480)) #initialize window to display
pygame.display.set_caption('Buildbot')
screen = pygame.display.get_surface() #the base display surface

pygame.mouse.set_visible(0)

background = pygame.Surface(screen.get_size()) #creates the background surface
background = background.convert()
background.fill((250, 250, 250))

if pygame.font:
    font = pygame.font.Font(None, 36) #new font object
    text = font.render("Cool game", 1, (10, 10, 10)) #returns the surface with text
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

#whiff_sound = load_sound('whiff.wav')
#punch_sound = load_sound('punch.wav')

#load the bot animations
imageList = [[[0] * 19] * 16] * 3
for sLoop in range(3): #sizes
  for dLoop in range(16): #directions
    for iLoop in range(19): #images
      imageList[sLoop][dLoop][iLoop] = load_image(os.path.join(str(sLoop), str(dLoop), str(iLoop + 1) + '.bmp'), -1)

bot = Bot(2)
allsprites = pygame.sprite.RenderPlain((bot,)) #add sprites to the sprite group
clock = pygame.time.Clock()
main()