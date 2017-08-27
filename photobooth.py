'''
Created on 15.12.2016

@author: Marius
'''


# Import of Modules

import pygame        #displaying contents on screen
from photobooth_settings            import black, white, red, num_keys, framerate, COM, lbl_choose_keys, up, down, right, left, space, t_disp, t_swipe, t_rand, t_move, t_hold, myfontsmall, yellow
from photobooth_imgproc             import countdown_img, img_combine
from photobooth_camcon              import post_method, start_liveview
from photobooth_disp                import disp_obj, disp_preview, calc_screen, disp_button, disp_chart, disp_img
from photobooth_keys                import set_keys, get_key, reset_inputdevices
from photobooth_serialreplacement   import Serialrep
import serial
import time
from PIL import Image
import ctypes
import codecs
import struct

#To stop windows from auto resizing
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

#Random
import random

random.seed()

#Check whether Serial connection is on port
try:
    Ser = serial.Serial(
        port=COM,
        baudrate=9600,
        timeout=0.01,
    )
except:
    Ser = Serialrep()

#Initialize pygame and set screen
pygame.init()

#ScreenTot = pygame.display.set_mode((800,450),pygame.HWSURFACE)
ScreenTot = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

buttonhold_org =        pygame.image.load('img/buttonhold.png').convert_alpha()
buttonhold_mask =       pygame.image.load('img/buttonhold_mask.png').convert_alpha()

Info = pygame.display.Info() #Contains screen-size information

ExtScreen = calc_screen(ScreenTot,Info)

#Fill Background Color
ExtScreen.fillbg()
pygame.display.flip()

try:
    post_method('startRecMode')
except:
    pygame.quit()
    print 'Check camera connection'
    raise SystemExit

#Aufgaben lesen

taskfile = codecs.open('tasks.txt', 'r', 'iso-8859-15')
lines = list()
for i in taskfile.readlines():
    lines.append(i.rstrip('\r\n'))

#---------------------------------------------------------- #Connect with camera

disp_obj(lbl_choose_keys,ExtScreen,white)

#Saves objects for the wished number of keys
keys = set_keys(pygame,Ser,num_keys)

#Initialize Clock
Clock = pygame.time.Clock()

ticks_st = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s))

img_num = 0

ticks_move_st_1 = 0
ticks_move_st_2 = 0 
 
#Wait  for Key press
while True:
      
    #Limit framerate
    Clock.tick(framerate)
 
    #random 1
    x = random.randint(1,t_rand*framerate)
    if x == t_rand*framerate and ticks_move_st_1 == 0:
        ticks_move_st_1 = pygame.time.get_ticks()
        ExtScreen.move_1 = 1
        ExtScreen.moved = 1
    elif pygame.time.get_ticks() >= ticks_move_st_1 + t_move*1000 and ticks_move_st_1 != 0:
        ticks_move_st_1 = 0
        ExtScreen.move_1 = 0
        ExtScreen.moved = 1
    else:
        ExtScreen.moved = 0
 
    #random 2
    x = random.randint(1,t_rand*framerate)
    if x == t_rand*framerate and ticks_move_st_2 == 0:
        ticks_move_st_2 = pygame.time.get_ticks()
        ExtScreen.move_2 = 1
        ExtScreen.moved = 1
    elif pygame.time.get_ticks() >= ticks_move_st_2 + t_move*1000 and ticks_move_st_2 != 0:
        ticks_move_st_2 = 0
        ExtScreen.move_2 = 0
        ExtScreen.moved = 1
    else:
        ExtScreen.moved = 0
     
    #Get pressed key
    i = get_key(pygame,Ser,keys,num_keys)
     
    ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
             
    if disp_chart(ExtScreen,ticks_st,ticks_en,t_swipe): #returns True if time reached
        ticks_st = pygame.time.get_ticks()
        img_num -= 1
        img_num = disp_img(ExtScreen,img_num)
    #if i >= 0:
    #    disp_obj(str(i),Screen,Info,white)
 
    #Take new image
    if i == 0:
         
        buttonhold = buttonhold_org.copy()
    
        time.sleep(0.3)
        
        tick_st = pygame.time.get_ticks()
        
        TransSurf = pygame.Surface((ExtScreen.width,ExtScreen.height),pygame.SRCALPHA)
        TransSurf.fill((0,0,0,128))
        
        show_hold_button = 0
        
        while keys[0].check_hold(pygame,Ser):
             
            percent = float(pygame.time.get_ticks() - tick_st)/(t_hold*1000)
             
            if percent >= 1:
                disp_obj(myfontsmall.render(lines[int(random.uniform(-0.5,len(lines)-0.501))], True, yellow),ExtScreen)
                time.sleep(1)
                break
            
            if percent >= 0.05:
             
                if show_hold_button == 0:
                    ExtScreen.blit(TransSurf)
                    pygame.display.flip()
                    show_hold_button = 1
                    
                pygame.draw.rect(buttonhold,red,pygame.Rect(35,255-percent*165,330,percent*165))
                buttonhold.blit(buttonhold_mask,(35,90))
                disp_obj(buttonhold,ExtScreen,white,2)
            
            #Limit framerate
            Clock.tick(framerate)
             
            pygame.event.get()
 
        #Try connecting to camera
        try:
            link = start_liveview()
        except:
            con = False
            while con == False:
                try:
                    link = start_liveview()
                    con = True
                except:
                    print 'Connection problem'
                    con = False
                    
                    keyres = get_key(pygame,Ser,keys,num_keys)
                    
                    print keyres == num_keys-1
                    
                    if keyres == num_keys-1:
                        con = True
                        exit
                        
        ExtScreen.fillbg()
        pygame.display.flip()
                         
        img_1 = countdown_img(ExtScreen,Ser,link,Clock,1)
        ExtScreen.fillbg()
        pygame.display.flip()
         
        img_2 = countdown_img(ExtScreen,Ser,link,Clock,2)
        #------------------------------------ img_2 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
         
        img_3 = countdown_img(ExtScreen,Ser,link,Clock,3)
        #------------------------------------ img_3 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
         
        img_4 = countdown_img(ExtScreen,Ser,link,Clock,4)
        #------------------------------------ img_4 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
         
        img_result, img_link = img_combine(ExtScreen,img_1,img_2,img_3,img_4)
         
        ExtScreen.disp_mode(0,1)
         
        disp_obj(img_result,ExtScreen,white,0)
         
        ticks_st = pygame.time.get_ticks()  #ticks for moment of start (=ms)/(1000ms/s)
         
        while True:
             
            #Limit framerate
            Clock.tick(framerate)
 
            ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
             
            if disp_chart(ExtScreen,ticks_st,ticks_en,t_disp): #returns True if time reached
                break
             
        reset_inputdevices(pygame,Ser,keys)
         
         
    elif i == 1:

        img_num -= 1
        ticks_st = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
         
        img_num = disp_img(ExtScreen,img_num)
         
    elif i == 2:
             
        img_num += 1
        ticks_st = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
         
        img_num = disp_img(ExtScreen,img_num)
 
    elif i == num_keys-1:
        break
         
pygame.quit()
