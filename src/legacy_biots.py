import pygame
import random
import math
from Box2D import b2Vec2
from compiler.ast import nodes

PIXEL_SCALE = 10 #just guessing here

background_colour = (255,255,255)
(width, height) = (800, 600)

vectorBiot = {}


def genBiot(angle=math.pi/2, depth=1,color=(0,0,0),parent=None):
    if depth:
        v1 = b2Vec2(math.cos(angle),math.sin(angle)) * depth
        vectorBiot[v1] = parent
        genBiot(angle=angle - (2*math.pi/10), depth=depth - 1,parent=v1)
        genBiot(angle=angle + (2*math.pi/10), depth=depth - 1,parent=v1)
        

def computeParentOffset(node,x,y):        
    if(vectorBiot.get(node)):
        (px,py) = computeParentOffset(vectorBiot.get(node),x,y)
        px += vectorBiot.get(node).x
        py += vectorBiot.get(node).y
        return (px,py)
    else:
         return (x,y)

def drawVectorBiot(x,y):
    color = (0,0,0)
    for (node,parent) in vectorBiot.iteritems():
        
        (px, py) = computeParentOffset(node,x,y)
        
        x1 = int(px*PIXEL_SCALE)
        y1 = int(py*PIXEL_SCALE)
        x2 = int(node.x * PIXEL_SCALE) + x1
        y2 = int(node.y * PIXEL_SCALE) + y1
                
        pygame.draw.line(screen, color, (x1,y1), (x2,y2), 1)
         

pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Biots')

mytext = font.render('THIS IS MY TEXT', True, (0,0,0))


running = True
while running:
    #check if we need to exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
    screen.fill(background_colour)
    genBiot(depth=3)
    drawVectorBiot(20, 10)
    genBiot(depth=3,angle=5*math.pi/12)
    drawVectorBiot(20, 10)
    #do the flip
    screen.blit(mytext,(20,20))
    pygame.display.flip()
