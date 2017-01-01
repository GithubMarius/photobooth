'''
Created on 15.12.2016

@author: Marius
'''


# Import of Modules

import pygame        #displaying contents on screen
from photobooth_settings            import black, white, num_keys, framerate, COM, lbl_choose_keys, up, down, right, left, space, t_disp, t_swipe
from photobooth_imgproc             import countdown_img, img_combine
from photobooth_camcon              import post_method, start_liveview
from photobooth_disp                import disp_obj, disp_preview, calc_screen, disp_button, disp_chart, disp_img
from photobooth_keys                import set_keys, get_key
from photobooth_serialreplacement   import Serialrep
import serial
import time
from PIL import Image

#Check whether Serial connection is on port
try:
    Ser = serial.Serial(
        port=COM,
        baudrate=9600,
        timeout=0.01,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )
except:
    Ser = Serialrep()

#Initialize pygame and set screen
pygame.init()

ScreenTot = pygame.display.set_mode((1100,700))
#------------------ ScreenTot = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

Info = pygame.display.Info() #Contains screen-size information

ExtScreen = calc_screen(ScreenTot,Info)

#Fill Background Color
ExtScreen.fillbg()
pygame.display.flip()


#---------------------------------------------------------- #Connect with camera
#--------------------------------------------------- post_method('startRecMode')

disp_obj(lbl_choose_keys,ExtScreen,white)

#Saves objects for the wished number of keys
keys = set_keys(pygame,Ser,num_keys)

#Initialize Clock
Clock = pygame.time.Clock()

ticks_st = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)

img_num = 0
2
#Wait for Key press
while True:
    
    #Limit framerate
    Clock.tick(framerate)
        
    #Get pressed key
    i = get_key(pygame,keys,num_keys)
    
    ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
            
    if disp_chart(ExtScreen,ticks_st,ticks_en,t_swipe): #returns True if time reached
        ticks_st = pygame.time.get_ticks()
        img_num -= 1
        img_num = disp_img(ExtScreen,img_num)
    #if i >= 0:
    #    disp_obj(str(i),Screen,Info,white)

    #Take new image
    if i == 0:
        
        #------------------------------------------------------------------ try:
            #------------------------------------------- link = start_liveview()
        #--------------------------------------------------------------- except:
            #------------------------------------------------------- con = False
            #----------------------------------------------- while con == False:
                #---------------------------------------------------------- try:
                    #----------------------------------------------- con == True
                    #------------------------------- post_method('startRecMode')
                #------------------------------------------------------- except:
                    #-------------------------------- print 'Connection problem'
                    #---------------------------------------------- con == False
#------------------------------------------------------------------------------ 
                    #----------- if get_key(pygame,keys,num_keys) == num_keys-1:
                        #-------------------------------------------------- exit
                        
        #----------------------- img_1 = countdown_img(Screen,Info,link,Clock,1)
        img_1 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
        
        #----------------------- img_2 = countdown_img(Screen,Info,link,Clock,2)
        img_2 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
        
        #----------------------- img_3 = countdown_img(Screen,Info,link,Clock,3)
        img_3 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
        
        #----------------------- img_4 = countdown_img(Screen,Info,link,Clock,4)
        img_4 = Image.open('img/test.jpg')
        ExtScreen.fillbg()
        pygame.display.flip()
        
        img_result, img_link = img_combine(ExtScreen,img_1,img_2,img_3,img_4)
        
        ExtScreen.disp_mode()
        
        disp_obj(img_result,ExtScreen,white,0)
        
        ticks_st = pygame.time.get_ticks()  #ticks for moment of start (=ms)/(1000ms/s)
        
        while True:
            
            #Limit framerate
            Clock.tick(framerate)

            ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
            
            if disp_chart(ExtScreen,ticks_st,ticks_en,t_disp): #returns True if time reached
                break
            
        pygame.event.clear()   

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
