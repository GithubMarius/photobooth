'''
Created on 16.12.2016

@author: Marius
'''

import pygame
import struct
from PIL import Image
from SonyPhotobooth.Disp        import dispPreview, dispObj
from SonyPhotobooth.Settings    import white, t, lbl_smile, x_space, y_space, col_w, prevIso, prevF, prevS
import os
import time

#try:
#    import urllib2
#except ImportError:
#    import urllib as urllib2

import urllib

def countdownImg(ExtScreen,Camera,Config,State,Ser,Clock,pos): #Gives countdown and takes image
    
    if Config.get('Settings','externalFlash') == 1:
        Camera.postMethod('setIsoSpeedRate',  [prevIso])
        Camera.postMethod('setFNumber',       [prevF])
        Camera.postMethod('setShutterSpeed',  [prevS])
        
    stream = urllib.request.urlopen(Camera.link)

    t_st = pygame.time.get_ticks()/1000 #ticks for moment of start (=ms)/(1000ms/s)
    cd_prev = t #Needed to see,whether new countdown number

    while True:
        
        time.sleep(.05)

        Ser.write(struct.pack('!B',0))
        Ser.write(struct.pack('!B',int(cd_prev)))
        
        #Limit framerate
        Clock.tick()

        t_en = pygame.time.get_ticks()/1000 #ticks for moment of start (=ms)/(1000ms/s)
    
        cd = int(t_st-t_en+t) #countdown
    
        if cd > 0:
            
            pygameImg = Camera.readImgBytes(stream)

            if cd_prev != cd:
                ExtScreen.fillbg(False)

            Rect = dispPreview(pygameImg,ExtScreen,pos)
            
            dispObj(str(cd),ExtScreen,white,0,Rect)
                                        
            cd_prev = cd
        
        else:
            Ser.write(struct.pack('!B',1))
            Ser.write(struct.pack('!B',2))
            Ser.write(struct.pack('!B',3))
            break

    if Config.get('Settings','externalFlash') == 1:
        Camera.postMethod('setIsoSpeedRate',[State.takeIso])
        Camera.postMethod('setFNumber',[State.takeF])
        Camera.postMethod('setShutterSpeed',[State.takeS])

    #Display smiley
    dispObj(lbl_smile,ExtScreen,white,1)
    
    stream.close()
    
    #Take picure, receive it and return
    img_res = Camera.takePhoto()
        
    Ser.write(struct.pack('!B',0))
    
    ExtScreen.fillbg()
    
    return img_res

def imgCombine(ExtScreen,Imgs): #combines 4 images to one and returns the results

    x = ExtScreen.width/2 - col_w
    y = ExtScreen.height/2

    o_width, o_height = Imgs[0].size

    n_width = x-1.5*x_space
    n_height = y-1.5*y_space

    scale_factor = min(n_width/o_width,n_height/o_height)

    s_width = scale_factor * o_width
    s_height = scale_factor * o_height

    r_width = 3 * x_space + 2 * s_width
    r_height = 3 * y_space + 2 * s_height

    size = int(s_width),int(s_height)

    result = Image.new("RGB", (int(r_width), int(r_height)), "white")
    
    for i in range(0,4):
        Imgs[i] = Imgs[i].resize(size)

    result.paste(Imgs[0],(int(x_space),int(y_space)))
    result.paste(Imgs[1],(int(2 * x_space + s_width),int(y_space)))
    result.paste(Imgs[2],(int(x_space),int(2 * y_space + s_height)))
    result.paste(Imgs[3],(int(2 * x_space + s_width),int(2 * y_space + s_height)))

    img_num_folder = str(len(os.listdir("results")) + 1)

    img_link = "results/result" + img_num_folder + ".jpg"

    result.save(img_link)

    img_mode = result.mode
    img_size = result.size
    img_data = result.tobytes()

    img_pg = pygame.image.fromstring(img_data,img_size,img_mode)
    
    return img_pg #, img_link