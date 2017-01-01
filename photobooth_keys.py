'''
Created on 16.12.2016

@author: Marius
'''
#from warnings import catch_warnings

from itertools import repeat

def set_keys(pygame,Ser,num_keys):
    
    #reset buffer
    Ser.reset_input_buffer()
    keys = []
    
    for _ in repeat(None, num_keys):
        w = True
        while w == True:
            if Ser.in_waiting > 0:
                keys.append(Baud_button(Ser))
                break
            else:
                for event in pygame.event.get():
    
                    if int(event.type) in [2,5]:
                        keys.append(Key(event))
                        w = False
                        
    return keys

def get_key(pygame,keys,num_keys):

    eventlist = pygame.event.get()
    
    ret = -1
    
    for i in range(0,num_keys):
        
        if keys[i].check_press(eventlist) == True:
            
            ret = i
            
    return ret


class Key:
        
    def __init__(self,event):
        
        self.type = event.type
        
        if event.type == 2:
            self.identifier = event.key
        else:
            self.identifier = event.button
    
    def check_press(self,eventlist):
        
        for event in eventlist:
            
            if event.type == self.type:
                                
                if (event.type == 2 and self.identifier == event.key) or (event.type == 5 and self.identifier == event.button):
                    
                    return True
                
        return False
                
                

class Baud_button:
    
    def __init__(self,Ser):
        self.Ser = Ser
        self.num = int(self.Ser.read(8))
        
    def check_press(self,*var):
                        
        if self.Ser.inWaiting() > 0:
            
            #Receive data and check whether is int
            try:
                rec = int(self.Ser.read(8))
            except:
                rec = 0

            #self.ser.reset_input_buffer()
                        
            #Return status
            if rec == 1:
                return True
            else:
                return False
            
        else:
            
            return False