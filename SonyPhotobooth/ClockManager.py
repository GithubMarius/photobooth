'''
Created on 21.01.2018

@author: Marius
'''
from pygame.time import Clock, get_ticks #@UnresolvedImport

#Uses pygames Clock two deal with timemanagement
class ClockManager():
    
    def __init__(self,framerate):
        self.Clock = Clock()
        
    def tick(self):
        self.Clock.tick()
        
    def getT(self):
        return get_ticks()
    
    def start(self):
        self.ticksStart = self.getT()
        
    def ticksDiff(self):
        return self.getT()-self.ticksStart