'''
Created on 16.12.2016

@author: Marius
'''

import pygame
import os
from photobooth_settings import myfont, yellow, white, col_w, x_space, y_space, preview_w, preview_h,buttonfont, black, space, left, right, lbl_next, resultsfolder

#Extends existing Screen object with addiotional methods
class ExtendedScreen:
    
    def __init__(self,Screen,px,py,w,h):
    
        #Screen object
        self.Screen = Screen
        
        #Offset (x & y)
        self.offsetx = px
        self.offsety = py
        
        #Screen width and height
        self.width = w
        self.height = h
        
        #Create standard background
        self.Background = pygame.Surface((w,h))
        
        #Buttons
        self.space = space
        self.left = left
        self.right = right
        
        #Buttondescriptions
        #self.lbl_next = lbl_next
        
        #Background color
        self.Background.fill(white)
        
        #Show image No 1
        imgload = pygame.image.load('img/photobooth_person1.png').convert_alpha()
        imgload = pygame.transform.scale2x(imgload)
        self.Background.blit(imgload,(w-(0.5*(col_w+imgload.get_width())),0.5*(h-imgload.get_height())))
        
        #Show image No 2
        imgload = pygame.image.load('img/photobooth_person2.png').convert_alpha()
        imgload = pygame.transform.scale2x(imgload)
        self.Background.blit(imgload,(0.5*(col_w-imgload.get_width()),0.5*(h-imgload.get_height())))
        
    #Fills background with background color
    def fillbg(self):
        
        #self.Screen.fill(white)
        self.blit(self.Background)
    
    #Blits on Screen Object and gives correct Rect back
    def blit(self,obj,pos = (0,0)):
        
        Rect = self.Screen.blit(obj,pos)
        
        return Rect.move((self.offsetx,self.offsety))
    
    def disp_mode(self):
        
        self.fillbg()
        
        disp_button(self.space,self,1,mode = 1)
        disp_button(self.left,self,3,mode = 1)
        disp_button(self.right,self,4,mode = 1)
        #disp_button(self.lbl_next,self,4,mode = 2)
        
        pygame.display.flip()
    
def calc_screen(ScreenTot,Info):
    
    #Find smaller dimension (height or width)
    sc_w =  float(Info.current_w - 3*x_space - 2*col_w)/float(preview_w)
    sc_h = float(Info.current_h - 3*y_space)/float(preview_h)

    if sc_h < sc_w: #If too much horizontal space
        w = int(sc_h*preview_w + 3*x_space + 2*col_w)
        h = Info.current_h
    else: #If too much vertical space
        w = Info.current_w
        h = int(sc_w*preview_h + 3*y_space)

    #Calc main Surface position    
    px = (Info.current_w - w)/2
    py = (Info.current_h - h)/2
    
    #Create Subsurface
    Screen = ScreenTot.subsurface((px,py,w,h))
    
    #Save in extended Screen-class object
    ExtScreen = ExtendedScreen(Screen,px,py,w,h)
    
    return ExtScreen

def disp_obj(obj,ExtScreen,color = white,objtype = 1): #displays an object depending on the wanted position

    # objtype == 1 => Fill screen
    if objtype == 1:
        ExtScreen.fillbg()

    # isstring? => render font
    if isinstance(obj, basestring):
        obj = myfont.render(obj, True, yellow)
        
    #disp on screen
    Rect = ExtScreen.blit(obj, ((ExtScreen.width-obj.get_width())/2,(ExtScreen.height-obj.get_height())/2))
    
    #If objtype == 1, whole screen has to be updated
    if objtype != 1:
        pygame.display.update(Rect)
    else:
        pygame.display.flip()

#Display livestream from camera
def disp_preview(obj,ExtScreen,pos = 1):
    
    #fill white screen
    #Screen.fill(white)
    
    #calc position
    x = (ExtScreen.width - 2*col_w-3*x_space)/2
    y = (ExtScreen.height - 3*y_space)/2

    #scale fitting to screen size
    scale_factor = min(x/float(preview_w),y/float(preview_h))
    obj = pygame.transform.scale(obj,(int(scale_factor*preview_w),int(scale_factor*preview_h)))
    
    #Adjust position (left top, right top, bottom left, bottom right)
    if pos == 1:
        Rect = ExtScreen.blit(obj, (0.5*ExtScreen.width-int(scale_factor*preview_w)-0.5*x_space,0.5*ExtScreen.height-int(scale_factor*preview_h)-0.5*y_space))

    elif pos == 2:
        Rect = ExtScreen.blit(obj, (0.5*ExtScreen.width+0.5*x_space,0.5*ExtScreen.height-int(scale_factor*preview_h)-0.5*y_space))

    elif pos == 3:
        Rect = ExtScreen.blit(obj, (0.5*ExtScreen.width-int(scale_factor*preview_w)-0.5*x_space,0.5*ExtScreen.height+0.5*y_space))

    else:
        Rect = ExtScreen.blit(obj, (0.5*ExtScreen.width+0.5*x_space,0.5*ExtScreen.height+0.5*y_space))
    
    #Update display
    pygame.display.update(Rect)
    
#Display buttons (button icons)
def disp_button(obj,ExtScreen,pos = 1,mode = 1):

    if mode == 1:

        o_w = obj.get_width()/2
        o_h = obj.get_height()/2

    else:

        if mode == 2:
        
            obj = buttonfont.render(obj, True, black)
            obj = pygame.transform.rotate(obj,90)

        o_w = obj.get_width()/2

        if pos == 1 or pos == 2:

            o_h = -col_w/2
            
        else:

            o_h = obj.get_height() + col_w/2

    if pos == 1:

        x = col_w/2 - o_w
        y = col_w/2 - o_h

    elif pos == 2:

        x = ExtScreen.width - col_w/2 - o_w
        y = col_w/2 - o_h

    elif pos == 3:

        x = col_w/2 - o_w
        y = ExtScreen.height - col_w/2 - o_h

    else:

        x = ExtScreen.width - col_w/2 - o_w
        y = ExtScreen.height - col_w/2 - o_h
    
    Rect = ExtScreen.blit(obj,(x,y))
    
    #Update display
    pygame.display.update(Rect)
    
def disp_chart(ExtScreen,ticks_st,ticks_en,t):

    chart_pos = (ticks_en-ticks_st)*100/t/1000

    #Display time scale
    chart = pygame.Surface((100, 40))
    chart.fill(black)
    pygame.draw.rect(chart,white,pygame.Rect((100-chart_pos),0,100,40))

    #Print
    disp_button(chart,ExtScreen,2)
    
    if ticks_en-ticks_st >= t*1000:
        return True
    
    return False

def disp_img(ExtScreen,img_num):
    
    list_imgs = os.listdir(resultsfolder)
    len_imgs = len(list_imgs)
    
    if len_imgs == img_num:
        img_num = 0
    elif img_num < 0:
        img_num = len_imgs-1
    
    img = pygame.image.load(resultsfolder + '/' + list_imgs[img_num])
    
    disp_obj(img,ExtScreen)
    
    return img_num