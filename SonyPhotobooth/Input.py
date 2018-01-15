'''
Created on 16.12.2016

@author: Marius
'''
#from warnings import catch_warnings

from itertools import repeat
from pygame import KEYDOWN, MOUSEBUTTONDOWN #@UnresolvedImport

def setKeys(pygame,Ser,num_keys):
    
    #reset buffer
    Ser.reset_input_buffer()
    keys = []
    
    for _ in repeat(None, num_keys):
        w = True
        while w == True:
            if Ser.in_waiting >= 2:
                #Check whether number = 0 at end or not (0 is not relevant)
                num = int(Ser.read(2))
                if num%10 != 0: #mod == 0 => only Offsignal
                    keys.append(Baud_button(Ser,num))
                    break
                #Check if keys were pressed
            else:
                for event in pygame.event.get():
    
                    if int(event.type) in [KEYDOWN,MOUSEBUTTONDOWN]:
                        keys.append(Key(event))
                        w = False
                        
        print(str(len(keys)) + ' Keys set')
        
    return keys

def getKey(pygame,Ser,keys,num_keys):

    eventlist = pygame.event.get()
    
    ret = -1
    ser_list = []
        
    while Ser.in_waiting >= 2:
        ser_list.append(Ser.read(2))
    
    for i in range(0,num_keys):
        
        if keys[i].checkPress(eventlist,ser_list) == True:
            
            ret = i
            
    return ret


class Key:
        
    def __init__(self,event):
        
        self.type = event.type
        
        if event.type == KEYDOWN:
            self.identifier = event.key
        else:
            self.identifier = event.button
    
    def checkPress(self,eventlist,*var):
        
        for event in eventlist:
                        
            if (event.type == KEYDOWN and self.identifier == event.key) or (event.type == MOUSEBUTTONDOWN and self.identifier == event.button):
                
                return True
                
        return False
    
    def checkHold(self,pygame,*var):
        
        return pygame.key.get_pressed()[self.identifier]
                
                

class Baud_button:
    
    def __init__(self,Ser,num):
        self.Ser = Ser
        self.num = num
        self.stat = 0
        
    def checkPress(self,ign,ser_list):

        for i in range(0,len(ser_list)):
            
            num_in = int(ser_list[i])

            if num_in == self.num:
                self.stat = 1
                return True
            
            elif num_in == self.num-1:
                self.stat = 0
                    
        return False
        
        #=======================================================================
        # #Receive data and check whether is int
        # try:
        #     rec = 0 #int(self.Ser.read(2))
        #     
        #     if rec == self.num:
        #         self.stat = 1
        #         return True
        #         
        #     elif rec == self.num-1:
        #         self.stat = 0
        #     
        # except:
        #     pass
        # 
        # return False
        #=======================================================================

        #self.ser.reset_input_buffer()
                    
        
    def checkHold(self,ign,Ser):
        
        while Ser.in_waiting >= 2:
            num_in = int(Ser.read(2))
            if num_in == self.num-1:
                self.stat = 0
                
        return self.stat
        
def resetInputDevices(pygame,Ser,Keys):
    
    pygame.event.clear()
    Ser.reset_input_buffer()
    
    for key in Keys:
        if isinstance(key,Baud_button):
            key.stat = 0