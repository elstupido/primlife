import pygame
import random
import math
from Box2D import b2Vec2
from biots.genes import genRandomBiotGene, mutate
from biots.biot_paramaters import BiotParams



global PIXEL_SCALE
PIXEL_SCALE = 1 #just guessing here

#BIOT MAX DEPTH
MAX_DEPTH = 6
DEBUG = False

bp = BiotParams()


background_colour = (0,0,0)
(width, height) = (1200, 700)

gravity = (math.pi, 0.002)
use_gravity = False
drag = 0.989
elasticity = 0.75
max_speed = 6

pygame.init()

debug_font = pygame.font.Font(pygame.font.match_font('calibri'),12)


def addVectorsB2(vec1, vec2):
    (angle1, length1) = vec1
    (angle2, length2) = vec2
    
#     v1= b2Vec2(x,y)
#     v2= b2Vec2(x2,y2)
#     v3 = v1 * length1 + v2 * length2
#     b2angle = math.atan2(v3.x,v3.y)
#     b2length = math.hypot(v3.x,v3.y)    
    
    #now faster with box2d!
    v1 = b2Vec2(length1*math.sin(angle1), length1*math.cos(angle1))
    v2 = b2Vec2(length2*math.sin(angle2), length2*math.cos(angle2))

    v3 = v1 + v2
        
    b2angle = math.atan2(v3.x,v3.y)
    b2length = math.hypot(v3.x,v3.y)

    return (b2angle, b2length)

#this is black mojo from the internets
#thanks to this guy: http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
#
# # The solution involves determining if three points are listed in a counterclockwise order. 
# # So say you have three points A, B and C. 
# # If the slope of the line AB is less than the slope of the line AC 
# # then the three points are listed in a counterclockwise order.
# 
# # These intersect if and only if points A and B are separated by segment CD and points C and D are separated by segment AB. 
# # If points A and B are separated by segment CD then ACD and BCD should have opposite orientation 
# # meaning either ACD or BCD is counterclockwise but not both.
# 
# #This algorithm assumes the endpoints are not closed thus a test for collinearity is required to be complete.
#
#this means if two biots segments intersect exactly parallel to each other, we dont detect collision. 
#its FAST and works most of the time, good enough for now 
 
def line_intersection(line1, line2):
    A = line1[0] #x1,y1
    B = line1[1] #x2,y2
    C = line2[0] #x3,x4
    D = line2[1] #x5,x6
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
    
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    


def addVectors(vec1, vec2):
    (angle1, length1) = vec1
    (angle2, length2) = vec2
    x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
    
    angle = 0.5 * math.pi - math.atan2(y, x)
    length  = math.hypot(x, y)

    return (angle, length)

def collide(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    
    if p1.boundingBox.colliderect(p2.boundingBox):
        if p1.collide(p2):
            tangent = math.atan2(dy, dx)
            angle = 0.5 * math.pi + tangent
    
            angle1 = 2*tangent - p1.angle
            angle2 = 2*tangent - p2.angle
            speed1 = p2.speed*elasticity
            speed2 = p1.speed*elasticity
    
            (p1.angle, p1.speed) = (angle1, speed1)
            (p2.angle, p2.speed) = (angle2, speed2)
    
            p1.x += math.sin(angle)
            p1.y -= math.cos(angle)
            p2.x -= math.sin(angle)
            p2.y += math.cos(angle)
#             angle = math.atan2(dy, dx) + 0.5 * math.pi
#             total_mass = p1.mass + p2.mass
#             (p1.angle, p1.speed) = addVectors((p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass), (angle, 2*p2.speed*p2.mass/total_mass))
#             (p2.angle, p2.speed) = addVectors((p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass), (angle+math.pi, 2*p1.speed*p1.mass/total_mass))
#             p1.speed *= elasticity
#             p2.speed *= elasticity
  

class Biot:
    #a biot is a collection of segments
    
    MAX_SEGMENTS = bp.MAX_SEGMENTS
    MAX_SYMMETRY = bp.MAX_SYMMETRY
    
    def __init__(self,x,y,father=None):
        
        self.x = x
        self.y = y
        self.angle = math.pi 
        self.speed = 0
        self.size = 60
        self.mass = 30
        self.boundingBox = pygame.Rect(0,0,0,0)
        self.arms = []
        self.initial_energy = 0
        self.updated = 0
        self.MAX_UPDATES = bp.MAX_UPDATES
        self.extraEnergy = 0
        if father:
            biotGene = mutate(father)
        else:
            #generating new biot
            biotGene = genRandomBiotGene()
        
        self.gene = biotGene
        
        for arm in range(biotGene['num_arms']):
            self.arms.append(BiotArm(self.x*(1/PIXEL_SCALE),self.y*(1/PIXEL_SCALE),size=biotGene['size'],gene=biotGene['armGenes'][arm]))
        
        for a in self.arms:
            self.initial_energy += a.getEnergy()       
    
    def isDead(self):
        dead = True
        for a in self.arms:
            dead = dead and a.isDead()
        if self.updated >= self.MAX_UPDATES:
            return True
        return dead 
    
    def move(self):
        if use_gravity:
            (self.angle, self.speed) = addVectors((self.angle, self.speed), gravity)
        for my_arm in self.arms:
            for node1,info in [ (node1,info) for node1,info in my_arm.idBiot.items() if my_arm.idBiot[node1]['exists'] ]:
                if info['color'] == (0,255,255):
                    if info['movecounter'] < 1:
                        if info['seg_id'] > max(my_arm.gene.get('segGenes').keys()):
                            print("IM BAAAAAACK")
                            print("MISMATCH! %s %s" % (info['seg_id'], max(my_arm.gene.get('segGenes').keys())))
                        (self.angle,self.speed) = addVectors((self.angle, self.speed), (info['node'] * info['length']) )
                        info['movecounter'] = my_arm.gene.get('segGenes').get(info['seg_id']).get('movecounter')
                        if self.speed > max_speed:
                            self.speed = max_speed
                    else:
#                         print info['movecounter']
                        info['movecounter'] -= 1

                
                        
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.speed *= drag
        
        
    def findArm(self,x,y,):
        if DEBUG:
            print("me: %s %s mouse: %s %s" % (self.x, self.y, x, y))
        if self.boundingBox.collidepoint(x, y):
           return self

    def bounce(self):
        if self.x > width:
            self.x = self.size +10
            self.speed *= elasticity

        elif self.x < self.size:
            self.x = (width - self.size)
            self.speed *= elasticity

        if self.y > height - self.size:
            self.y = self.size + 10
            self.speed *= elasticity

        elif self.y < self.size:
            self.y = (height - self.size)
            self.speed *= elasticity



    def collide(self,other_biot):
#         sleep = 0.01
#         if (self.speed < sleep) and (other_biot.speed < sleep):
#             return False
        result = self.collide_line(other_biot)
        if result:
            (my_arm,your_arm,node1,node2) = result
            if my_arm.idBiot[node1]['color'] == (255,0,0):
                if DEBUG:
                    print("destroying Nodes: %s " % (node2))
                if your_arm.idBiot[node2]['energy'] < bp.DEATH_ENERGY:
                    your_arm.destroyNode(node2)
                    your_arm.idBiot[node2]['energy'] = 0
                else:
                    your_arm.idBiot[node2]['energy'] -= bp.ENERGY_LOST_FROM_ATTACK
                    my_arm.idBiot[node1]['energy'] += bp.ENERGY_GAINED_FROM_ATTACK
            elif my_arm.idBiot[node1]['color'] == (0,255,0):
                my_arm.destroyNode(node1) 
            if your_arm.idBiot[node2]['color'] == (255,0,0):
                if DEBUG:
                    print("destroying Nodes: %s " % (node1))
                if my_arm.idBiot[node1]['energy'] < bp.DEATH_ENERGY:
                    my_arm.destroyNode(node1)
                    my_arm.idBiot[node1]['energy'] = 0
                else:
                    my_arm.idBiot[node1]['energy'] -= bp.ENERGY_LOST_FROM_ATTACK
                    your_arm.idBiot[node2]['energy'] += bp.ENERGY_GAINED_FROM_ATTACK
            elif your_arm.idBiot[node2]['color'] == (0,255,0):
                your_arm.destroyNode(node2)
            return True
        else:
            return False

#TODO: there has got to be a way to make this faster
    def collide_line(self,other_biot):
        for my_arm in self.arms:
            for node1,line1 in [ (node1,line1) for node1,line1 in my_arm.points.items() if my_arm.idBiot[node1]['exists'] ]:
                for your_arm in other_biot.arms:
                    for node2,line2 in [ (node2,line2) for node2,line2 in your_arm.points.items() if your_arm.idBiot[node2]['exists'] ]:
                        if line_intersection(line1, line2):
                            return (my_arm,your_arm,node1,node2)
                            
    def reproduce(self):
        energy = 0
        for a in self.arms:
            energy += a.extraEnergy
        if energy > self.initial_energy * bp.REPRODUCTION_RATE:
            self.extraEnergy = 0
            self.updated = self.MAX_UPDATES
            for a in self.arms:
                a.extraEnergy = 0
            return True
        else:
            return False            

    def rebalanceArmEnergy(self):
        energy = 0
        for a in self.arms:
            energy += a.extraEnergy
        self.extraEnergy = energy
        energy = energy / len(self.arms)
        for a in self.arms:
            a.extraEnergy = energy

    def update(self):
        self.updated += 1
        self.move()
        self.bounce()
        self.boundingBox = None
        self.rebalanceArmEnergy()
        status_str = ""
        for arm in self.arms:
            #arm.drawTree(self.x,self.y,None,4)
            arm.caclulateEnergyGain()
            arm.rebalanceEnergy()
            arm.drawVectorBiot(self.x,self.y)
            if self.boundingBox:
                self.boundingBox.union_ip(pygame.Rect(arm.minx,arm.miny,arm.maxx-arm.minx,arm.maxy-arm.miny))
                #pygame.polygon(screen, (0,0,0), [(arm.maxx,arm.maxy),(arm.maxx,arm.miny),(arm.minx,arm.miny),(arm.minx,arm.maxy)],2))
            else:
                self.boundingBox = pygame.Rect(arm.minx,arm.miny,arm.maxx-arm.minx,arm.maxy-arm.miny) 
                #pygame.draw.polygon(screen, (0,0,0), [(arm.maxx,arm.maxy),(arm.maxx,arm.miny),(arm.minx,arm.miny),(arm.minx,arm.maxy)],2)
        if DEBUG:
            status_str += str("energy -> %s  age -> %s" % (self.extraEnergy,self.updated))
            status_text = debug_font.render(status_str, True, (255,255,255))
            screen.blit(status_text,(self.boundingBox.x,self.boundingBox.y))
            pygame.draw.rect(screen, (0,0,255), self.boundingBox, 1)


class BiotArm:
    
    def __init__(self, x, y,size=15,gene={}):
        self.x = x
        self.y = y
        self.size = size
        self.gene = gene
        self.drawAngle = self.gene['angle']
        self.segmentMaxEnergy = bp.MAX_SEGMENT_ENERGY
        self.segmentMinEnergy = bp.MIN_SEGMENT_ENERGY
        
        self.idBiot = {}
        self.points = {}
        
        self.maxx = None
        self.maxy = None
        self.minx = None
        self.miny = None
        
        self.boundingBox = None
        self.extraEnergy = 0
        
        self.genBiot(angle=self.drawAngle,level=self.gene['num_levels']-1)

    def getEnergy(self):
        energy = 0
        for seg, info in self.idBiot.items():
            energy += info['energy']
        return energy

    def caclulateEnergyGain(self):
        for node, info in [ (node, info) for node,info in self.idBiot.items() if info['exists']]:
            if info['color'] == (0,255,0):
                info['energy'] -= bp.GREEN_LOSS_PER_TICK
            elif info['color'] == (255,0,0):
                info['energy'] -= bp.RED_LOSS_PER_TICK
            elif info['color'] == (0,0,255):
                info['energy'] -= bp.BLUE_LOSS_PER_TICK
            elif info['color'] == (0,255,255):
                info['energy'] -= bp.CYAN_LOSS_PER_TICK
            if info['energy'] < 10:
                self.destroyNode(node)
    
    def isDead(self):
        return not(bool([node for node, info in self.idBiot.items() if info['exists']]))
    
    def rebalanceEnergy(self):
        # energy is rebalanced across the tree
        # for each node, check energy
        # if > self.segementMaxEnergy take remainder and add to root.
        for info in [info for nodeid,info in self.idBiot.items() if nodeid != 'r' and info['energy'] > self.segmentMaxEnergy]:
            extra = info['energy'] - self.segmentMaxEnergy
            info['energy'] = self.segmentMaxEnergy
            self.idBiot['r']['energy'] += extra
        
        self.idBiot['r']['energy'] += self.extraEnergy
        self.extraEnergy = 0
        # then, rebalance energy across biot by pushing > self.segmentMaxEnergy 
        # to each child node recursively
        self._rebalanceEnergy('r')
        self.harvestExtraEnergy()
    
    def _rebalanceEnergy(self,node):
        for node2,armSegment in self.idBiot.items():
            if armSegment['parent_name'] == node:        
                if self.idBiot[node]['energy'] > self.segmentMaxEnergy:
                    extra = self.idBiot[node]['energy'] - self.segmentMaxEnergy
                    extra_by_child = extra / 2 #self.idBiot[node]['numchildren']
                    self.idBiot[node2]['energy'] += extra_by_child
                    self.idBiot[node]['energy'] = self.segmentMaxEnergy + extra_by_child
                    if self.idBiot[node2]['energy'] > 10:
                        self.idBiot[node2]['exists'] = True
        for node2,armSegment in self.idBiot.items():
            if armSegment['parent_name'] == node:
                self._rebalanceEnergy(node2)
    
    def harvestExtraEnergy(self):
        for node2, armSegment in self.idBiot.items():
            if node2 not in [ armSegment['parent_name'] for node,armSegment in self.idBiot.items() ]:
                if self.idBiot[node2]['energy'] > self.segmentMaxEnergy:
                    extra = self.idBiot[node2]['energy'] - self.segmentMaxEnergy
                    self.extraEnergy += extra
                    self.idBiot[node2]['energy'] = self.segmentMaxEnergy


    def genBiot(self,angle=math.pi/2, depth=2,color=(255,255,255),parent=None,level=1,name="r",parent_name=None):
        if level:
            gene = self.gene['segGenes'][level]
            branchfactor = gene['branchfactor']
            length = gene['length']
            
            v1 = b2Vec2(math.cos(angle),math.sin(angle)) * length

            self.idBiot[name] = {
                                  'parent_name'     : parent_name,
                                  'node'            : v1,
                                  'parent_vector'   : parent,
                                  'exists'          : True,
                                  'depth'           : depth,
                                  'level'           : level,
                                  'color'           : gene['color'],
                                  'energy'          : gene['energy'],
                                  'length'          : gene['length'],
                                  'movecounter'     : gene['movecounter'],
                                  'seg_id'          : level,
                                 } 
            
            self.genBiot(angle=angle - branchfactor,name=name + "m",level=level-1,parent=v1,parent_name=name)
            self.genBiot(angle=angle + branchfactor,name=name + "p",level=level-1,parent=v1,parent_name=name)
            
    def computeParentOffsetID(self,nodeid):
        if self.idBiot.get(nodeid):
            parentNodeId = self.idBiot.get(nodeid)['parent_name']
            node = self.idBiot.get(nodeid)['node']
            parent = self.idBiot.get(nodeid)['parent_vector']
        else:
            return (0,0)
        if nodeid != 'r':
            (px,py) = self.computeParentOffsetID(parentNodeId)
            px += parent.x
            py += parent.y
            return (px,py)
        else:
            return (0,0)

    
    
    def destroyNode(self,nodeid):
        self.idBiot[nodeid]['exists'] = False
        self.idBiot[nodeid]['energy'] = 0
        for nodeid2,armSegment in self.idBiot.items():
            if armSegment['parent_name'] == nodeid:
                self.destroyNode(nodeid2)
                
    
    def shouldBeDrawn(self,node):
        return self.existing_segments.get(node)

    
    def drawVectorBiot(self,x,y):
        color = (255,255,255)
        list_of_x = set()
        list_of_y = set()

        count = 0
        
        
        for nodeid, armSegment in sorted(self.idBiot.items()):
            
            node    = armSegment.get('node')
            exists  = armSegment.get('exists')
            color   = armSegment.get('color')

            
            (px,py) = self.computeParentOffsetID(nodeid)
            x1 = int(px*PIXEL_SCALE + x)
            y1 = int(py*PIXEL_SCALE + y)
            x2 = int(node.x * PIXEL_SCALE + x1)  
            y2 = int(node.y * PIXEL_SCALE + y1)

                  
            list_of_x.add(x1)
            list_of_x.add(x2)
            list_of_y.add(y1)
            list_of_y.add(y2)
            if exists:
                pygame.draw.line(screen, color, (x1,y1), (x2,y2), 1)
            self.points[nodeid] = ((x1,y1),(x2,y2))
            

        self.minx = sorted(list_of_x)[0]
        self.miny = sorted(list_of_y)[0]
        self.maxx = sorted(list_of_x,reverse=True)[0]
        self.maxy = sorted(list_of_y,reverse=True)[0]

global screen
screen = None

def main():
    global PIXEL_SCALE
    global screen  
    screen = pygame.display.set_mode((width, height))            
    pygame.display.set_caption('Biots')
    clock=pygame.time.Clock()
    TARGET_FPS = 30
    MAX_BIOTS = 100
    
    
    biots = [Biot(100,100)]
    
    def makeBiots(b,num):
        spacing = 50
        new_biots = []
        if b:
            father = b
        else:
            father = Biot(200,100)
        
        for baby in range(num):
            angle = (baby + 1) * math.pi * 1/(num / 2)
            x,y = (math.cos(angle)*spacing + father.boundingBox.x,math.sin(angle)*spacing+father.boundingBox.y)
            if not [b.findArm(x,y) for b in biots if b.findArm(x,y) is not None]:
    #             print "new biot %s,%s %s" % (x,y,[b.findArm(x,y) for b in biots if b.findArm(x,y) is not None])
                new_biots.append(Biot(x,y,father.gene))
        return new_biots
    
    selected_biot = None
    move_biot = None
     
    from timeit import default_timer as timer
     
    running = True
    while running:
        #check if we need to exit
                #wipe last frame
        screen.fill(background_colour)
        start = timer()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    PIXEL_SCALE -= 0.1
                elif event.button == 5:
                    PIXEL_SCALE += 0.1
                (mx, my) = pygame.mouse.get_pos()
                search = [b.findArm(mx,my) for b in biots if b.findArm(mx,my) is not None]
                if DEBUG:
                    print(search)
                if search:
                    selected_biot = search[0]
                    move_biot = search[0]
                else:
                    selected_biot = None  
            elif event.type == pygame.MOUSEBUTTONUP:
                move_biot = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    if DEBUG:
                        print("Generating New Biots")
                    biots = makeBiots(None,4)
         
        if selected_biot:
            if selected_biot in biots:
                pygame.draw.rect(screen, (0,0,255), selected_biot.boundingBox, 1)
                energy = debug_font.render("energy-> %s" % (selected_biot.extraEnergy), True, (255,255,255))
                age = debug_font.render("age-> %s" % (selected_biot.updated), True, (255,255,255))
                screen.blit(energy,(selected_biot.boundingBox.x,selected_biot.boundingBox.y))
                screen.blit(age, (selected_biot.boundingBox.x, selected_biot.boundingBox.y + energy.get_size()[1]))
     
        if move_biot:
            (mx, my) = pygame.mouse.get_pos()
            dx = mx - move_biot.x
            dy = my - move_biot.y
            move_biot.angle = 0.5*math.pi + math.atan2(dy,dx)
            move_biot.speed = math.hypot(dx,dy) * 0.1

         
        for i,b in enumerate(biots):
            if b.isDead():
    #             print "%s has died" % b
                biots.remove(b)
                continue
            b.update()
            for b2 in biots[i+1:]:
                collide(b, b2)
            if b.reproduce() and len(biots) < MAX_BIOTS:
                biots += makeBiots(b,2)
                
                
        if not biots:
           biots = makeBiots(None, 4)
        
        total_biots = debug_font.render('Total Biots: %s' % len(biots),False,(255,255,255) )
        screen.blit(total_biots,(1,1))
             
        end = timer()
        loop_timer = debug_font.render("time: %s" % round((end - start),3),False,(255,255,255) ) 
        screen.blit(loop_timer,(1,height-loop_timer.get_size()[1]))
        #do the flip
        pygame.display.flip()
        clock.tick(TARGET_FPS)

if __name__ == '__main__':
    main()
    
