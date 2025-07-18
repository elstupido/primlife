from random import Random, choice
import math

MAX_LEVELS = 4
HERIDITARY_WEIGHT = 0
MUTATED_WEIGHT = 1
random_negative = Random().randint(-1,1)
ran = Random()


def shouldMutate(random_num,mutate_range):
    (low,high) = mutate_range
    return low < random_num < high
    

def genRandomBiotGene():
    gene = {
                 'num_arms'         : ran.randint(2,6),
                 'branchfactor'     : (2*math.pi/ran.randint(2, 14)),
                 'size'             : ran.randint(2, 10),
                 'armGenes'         : {}
                 }
    gene['armGenes'] = genRandomArmGenes(gene['num_arms'])
    
    #always place arms equally far apart
    for arm,armgene in gene['armGenes'].items():
        gene['armGenes'][arm]['angle'] = (arm + 1) * math.pi * 1/(gene['num_arms'] / 2)
        
    return gene 

def genRandomArmGenes(num_arms):
    armGenes = {}
    for arm in range(num_arms):
        armGenes[arm] = {  'num_levels' : ran.randint(2,MAX_LEVELS),
                           'angle' : None,
                           'segGenes' : {},
                           'arm_id'    : arm
                        }
        armGenes[arm]['segGenes'] = genRandomSegmentGenes(armGenes[arm]['num_levels'])
    return armGenes

def genRandomSegmentGenes(num_levels):
    segGenes = {}
    for seg in range(num_levels):
        segGenes[seg] = { 'branchfactor' : _choose_value(None,[(2*math.pi/ran.randint(2, 14))]), 
                          'color'        : _get_color((0,255,0)), 
                          'length'       : _choose_value(None,[ran.randint(5, 20)]),
                          'energy'       : 0,
                          'seg_id'       : seg,
                          'movecounter'  : _choose_value(None,[ran.randint(3, 50)]),
                         }
        segGenes[seg]['energy'] = mutate_energy(segGenes[seg])
    return segGenes

def _choose_value(parentValue,mutatedValueList):
    parent = []
    mutated = []
    if parentValue:
        parent = [parentValue] * HERIDITARY_WEIGHT
    if mutatedValueList:
        mutated = mutatedValueList * MUTATED_WEIGHT
    return choice(parent + mutated)


def mutate(parentGene):
    if shouldMutate(ran.randint(1, 100000), (1,5000)):
        newGene = {}
        for key, value in parentGene.items():
            if key == 'armGenes':
                continue
            newGene[key] = eval('mutate_%s(parentGene)' % (key))
        newGene['armGenes'] = mutate_armGenes(parentGene,newGene['num_arms'])
        return newGene
    else:
        return parentGene

def mutate_num_arms(parentGene):
    parent_arms = parentGene['num_arms']
    new_arms = parent_arms + ( 1 * ran.randint(-1,1) )
    if new_arms < 2:
        new_arms = 2
    if new_arms > 6:
        new_arms = 6
    return _choose_value(parent_arms,[new_arms])

def mutate_branchfactor(parentGene):
    parent_branchfactor = parentGene['branchfactor']
    new_branchfactor = parent_branchfactor + 0.1 * random_negative
    return _choose_value(parent_branchfactor, [new_branchfactor])

def mutate_size(parentGene):
    return 30

def mutate_armGenes(parentGene,num_arms):

    newGene = {}
    for arm,armGene in parentGene['armGenes'].items():
        newGene[arm] = {}
        newGene[arm]['arm_id'] = arm
        newGene[arm]['angle'] = None
        newGene[arm]['num_levels'] = mutate_num_levels(armGene)
        newGene[arm]['segGenes'] = mutate_segGenes(armGene['segGenes'],newGene[arm]['num_levels'])
    
    #if we have more arms now, add some genes
    missing_arms = num_arms - max(newGene.keys())
    if missing_arms > 1:
        for arm in range(num_arms)[-1*missing_arms:]:
                newGene[arm] = genRandomArmGenes(1)[0]
                 
    #always place arms equally far apart
    for arm,armGene in newGene.items():
        newGene[arm]['angle'] = (arm + 1) * math.pi * 1/(num_arms / 2)
    
    return newGene

def mutate_num_levels(armGene):
    parent_levels = armGene['num_levels']
    newlevel = parent_levels + ( 1 * ran.randint(-1,1) )
    if newlevel > MAX_LEVELS:
        newlevel = MAX_LEVELS
    if newlevel < 2:
        newlevel = 2
    return _choose_value(parent_levels, [newlevel])
        

def mutate_segGenes(segGenes,num_levels):
    newGene = {}
    random_negative = ran.randint(-1,1)
    for seg, segGene in segGenes.items():
        newGene[seg] = {}
        newGene[seg]['color'] = mutate_color(segGene)
        newGene[seg]['energy'] = mutate_energy(segGene)
        newGene[seg]['length'] = mutate_length(segGene)
        newGene[seg]['branchfactor'] = mutate_branchfactor(segGene)
        newGene[seg]['movecounter'] = mutate_movecounter(segGene['movecounter'])
        newGene[seg]['seg_id'] = seg
    missing_levels = num_levels - max(newGene.keys())
    if missing_levels > 1:
        for level in range(num_levels)[-1*missing_levels:]:
            newGene[level] = genRandomSegmentGenes(1)[0] 
            
    return newGene

def mutate_movecounter(movecount):
    return _choose_value(movecount,[movecount + (random_negative * 10)])

def mutate_color(segGene):
    parentColor = segGene['color']
    return _get_color(parentColor)  

def _get_color(parentColor):
    if parentColor:
        parentColor = [parentColor]
    else:
        parentColor = []
    red = [(255,0,0)]
    green = [(0,255,0)]
    blue = [(0,0,255)]
    cyan = [(0,255,255)]
    biglist = parentColor * 100 + red * 2 + green * 1 + blue * 1 + cyan * 1
    return choice(biglist)  


def mutate_energy(segGene):
    if segGene['color'] == (0,255,0):
        return 10
    else:
        return 100

def mutate_length(segGene):
    parentLen = segGene['length']
    return _choose_value(parentLen, [parentLen + ( 1 * random_negative )] )

# 
# import pprint
# # pprint.pprint(genRandomBiotGene())
# pprint.pprint(mutate(genRandomBiotGene()))
