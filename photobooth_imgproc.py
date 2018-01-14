'''
Created on 16.12.2016

@author: Marius
'''

import pygame
import struct
from PIL import Image
from photobooth_camcon import take_picture, readImgBytes, post_method, start_liveview
from photobooth_disp import disp_preview, disp_obj
from photobooth_settings import white, t, framerate, lbl_smile, x_space, y_space, col_w, externalFlash, prevIso, prevF, prevS
import io
import os
import time

try:
    import urllib2
except ImportError:
    import urllib as urllib2 

def countdown_img(ExtScreen,Ser,link,Clock,pos,takeIso,takeF,takeS): #Gives countdown and takes image
            
    if externalFlash == 1:
        post_method('setIsoSpeedRate',[prevIso])
        post_method('setFNumber',[prevF])
        post_method('setShutterSpeed',[prevS])
        
    #Open stream
    try:
        stream = urllib2.urlopen(link)
    except AttributeError:
        stream = urllib2.request.urlopen(link)

    t_st = pygame.time.get_ticks()/1000 #ticks for moment of start (=ms)/(1000ms/s)
    cd_prev = t #Needed to see,whether new countdown number

    while True:
        
        time.sleep(.05)

        Ser.write(struct.pack('!B',0))
        Ser.write(struct.pack('!B',int(cd_prev)))
        
        #Limit framerate
        Clock.tick(framerate)

        t_en = pygame.time.get_ticks()/1000 #ticks for moment of start (=ms)/(1000ms/s)
    
        cd = int(t_st-t_en+t) #countdown
    
        if cd > 0:
            
            pygameImg = readImgBytes(stream)

            if cd_prev != cd:
                ExtScreen.fillbg()

            Rect = disp_preview(pygameImg,ExtScreen,pos)
            
            disp_obj(str(cd),ExtScreen,white,0,Rect)
                                        
            cd_prev = cd
        
        else:
            Ser.write(struct.pack('!B',1))
            Ser.write(struct.pack('!B',2))
            Ser.write(struct.pack('!B',3))
            break

    if externalFlash == 1:
        post_method('setIsoSpeedRate',[takeIso])
        post_method('setFNumber',[takeF])
        post_method('setShutterSpeed',[takeS])

    #Display smiley
    disp_obj(lbl_smile,ExtScreen,white,1)
    
    stream.close()
    
    #Take picure, receive it and return
    img_res = take_picture()
        
    Ser.write(struct.pack('!B',0))
        
    return img_res

def img_combine(ExtScreen,img_1,img_2,img_3,img_4): #combines 4 images to one and returns the results

    x = ExtScreen.width/2 - col_w
    y = ExtScreen.height/2

    o_width, o_height = img_1.size

    n_width = x-1.5*x_space
    n_height = y-1.5*y_space

    scale_factor = min(n_width/o_width,n_height/o_height)

    s_width = scale_factor * o_width
    s_height = scale_factor * o_height

    r_width = 3 * x_space + 2 * s_width
    r_height = 3 * y_space + 2 * s_height

    size = int(s_width),int(s_height)

    img_1 = img_1.resize(size)
    img_2 = img_2.resize(size)
    img_3 = img_3.resize(size)
    img_4 = img_4.resize(size)

    result = Image.new("RGB", (int(r_width), int(r_height)), "white")

    result.paste(img_1,(int(x_space),int(y_space)))
    result.paste(img_2,(int(2 * x_space + s_width),int(y_space)))
    result.paste(img_3,(int(x_space),int(2 * y_space + s_height)))
    result.paste(img_4,(int(2 * x_space + s_width),int(2 * y_space + s_height)))

    img_num_folder = str(len(os.listdir("results")) + 1)

    img_link = "results/result" + img_num_folder + ".jpg"

    result.save(img_link)

    img_mode = result.mode
    img_size = result.size
    img_data = result.tobytes()

    img_pg = pygame.image.fromstring(img_data,img_size,img_mode)
    
    return img_pg, img_link