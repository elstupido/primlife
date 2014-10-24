#!/usr/bin/python
#All the stuff you need to change biot behavior

class BiotParams:
    ##biot params
    MAX_SEGMENTS = 10
    MAX_SYMMETRY = 8
    #age
    MAX_UPDATES = 500
    #means you need extra > 150% * initial energy to reproduce
    REPRODUCTION_RATE = 1.50
    
    #segment attack/die params
    DEATH_ENERGY = 10
    ENERGY_LOST_FROM_ATTACK = 200
    ENERGY_GAINED_FROM_ATTACK = 500

    #biotArm params
    #any more than this and it goes to the extra energy bucket
    MAX_SEGMENT_ENERGY = 200
    MIN_SEGMENT_ENERGY = 100
    
    GREEN_LOSS_PER_TICK = -3
    RED_LOSS_PER_TICK = 1
    BLUE_LOSS_PER_TICK = 1
    CYAN_LOSS_PER_TICK = 1
    
    

