'''
Created on Dec 25, 2016

@author: marius
'''
## ATTENTION: Do not publish dropbox keys.

#Photobooth

#Author:        Marius Hofmann
#Issue-Date:    20-09-2015
#License:     This code is licensed under the GPLv3.

#Keys:

#   1. take picture/etc.
#   2. previous
#   3. next
#   4. upload

#To use all functions you need a dropbox account.

#Import libraries

import requests        #to communicate with the camera
import json            #to send json objects
import time        #time
import urllib2        #stream read out/urls
import struct        #to create/use structs
import pygame        #displaying contents on screen
import io        #stream read out
import Tkinter
import os
import dropbox        #dropbox upload
import PyQRNative    #to create qr codes

from dropbox import client
from PIL import Image

#Important data

#   secret

app_key =       'XXXXXXXXXXXXXXX'   #DO NOT PUBLISH - PERSONAL
app_secret =    'XXXXXXXXXXXXXXX'   #DO NOT PUBLISH - PERSONAL

#   Labels

lbl_take_photo =    'Take photo'
lbl_return =        'Return'
lbl_next =          'Next'
lbl_previous =      'Previous'
lbl_qr_code =       'QR code'
lbl_dropbox =       'Dropbox'
lbl_choose_keys =   'Choose keys'
lbl_go =            'Go!'
lbl_smile =         'Smile ;)'
lbl_wait =          'Please wait!'

#   Dimensions

col_w = 120

x_space = 30
y_space = 30

#   Camera

url = 'http://192.168.122.1:8080/sony/camera'

preview_w = 640
preview_h = 424

#   Colors

yellow = pygame.Color(0,128,0)
black = pygame.Color(0,0,0)
white = pygame.Color(255,255,255)

#   Time

m = 1 #1.5 #adjust to get rid of delays
t = 3 #countdown time

#   Image displaying

result_disp_time = 10

#   Number of needed keys

num_keys = 4;

#   Initialise other variables

keys, types, img_link = [], [], []

#Functions

#   Dropbox/Upload

def get_mode(app_key = [], app_secret = []): #Asks wether you want to use the dropbox function and connects if so
    while True:
        upload_mode = raw_input("Do you want to use the dropbox uploading function? (y/n) ")
        if upload_mode == "n":
            return {'mode':0}
        elif upload_mode == "y":

            root = Tkinter.Tk() #Needed to read out clipboard
            root.withdraw()

            # Get your app key and secret from the Dropbox developer website

            flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

            # Have the user sign in and authorize this token
            authorize_url = flow.start()

            root.clipboard_clear()
            root.clipboard_append(authorize_url)
            
            print '1. Go to: ' + authorize_url + ' (already in clipboard)'
            print '2. Click "Allow" (you might have to log in first)'
            print '3. Copy the authorization code into clipboard and confirm.'
            code = raw_input("Enter anything if the code is in the clipboard.").strip()
            code = root.clipboard_get()
            
            # This will fail if the user enters an invalid authorization code
            access_token, user_id = flow.finish(code)

            client = dropbox.client.DropboxClient(access_token)
            print 'linked account: ', client.account_info()
            return {'mode':1,'client':client}

def dropbox_upload(link):

    f = open(link, 'rb')
    name = link.split("/",1)[1]
    response = client.put_file(name, f)
    print 'uploaded: ', response
    db_link = client.media(name)
    return db_link['url']

#   QR-Code

def create_qr_code(string):

    qr = PyQRNative.QRCode(8, PyQRNative.QRErrorCorrectLevel.L)
    qr.addData(string)
    qr.make()
    qr_code = qr.makeImage()
    qr_code.save("qr_code.jpg")


    mode = qr_code.mode
    size = qr_code.size
    data = qr_code.tostring()

    qr_code = pygame.image.fromstring(data, size, mode)
    
    return qr_code

#   Camera communication

def post_method(method,par = []): #general post_method for communication with camera

    payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    requests.post(url, data=data)

def take_picture(): #take one image and receive it

    method = 'actTakePicture'
    par = []

    payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    resp = requests.post(url, data=data)
    resp_js = resp.json()
    res_con = str(resp_js.get('result')[0][0])

    return res_con

def start_liveview(): #start camera liveview

    method = 'startLiveview'
    par = []

    payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    resp = requests.post(url, data=data)
    resp_js = resp.json()
    link = str(resp_js.get('result')[0])

    return link

#   Layout and displaying elements

def disp_obj(obj,type = 1): #displays an object depending on the wanted position

    if type >= 1:
    
        if type == 1:
            screen.fill(white)

        obj = myfont.render(obj, True, yellow)

    screen.blit(obj, ((screen_w-obj.get_width())/2,(screen_h-obj.get_height())/2))

    pygame.display.flip()

def disp_preview(obj,pos = 1):

    screen.fill(white)
    
    x = (screen_w - 2*col_w-3*x_space)/2
    y = (screen_h - 3*y_space)/2

    scale_factor = min(x/float(preview_w),y/float(preview_h))

    obj = pygame.transform.scale(obj,(int(scale_factor*preview_w),int(scale_factor*preview_h)))
    
    if pos == 1:

        screen.blit(obj, (0.5*screen_w-int(scale_factor*preview_w)-0.5*x_space,0.5*screen_h-int(scale_factor*preview_h)-0.5*y_space))

    elif pos == 2:

        screen.blit(obj, (0.5*screen_w+0.5*x_space,0.5*screen_h-int(scale_factor*preview_h)-0.5*y_space))

    elif pos == 3:

        screen.blit(obj, (0.5*screen_w-int(scale_factor*preview_w)-0.5*x_space,0.5*screen_h+0.5*y_space))

    else:

        screen.blit(obj, (0.5*screen_w+0.5*x_space,0.5*screen_h+0.5*y_space))

    pygame.display.flip()

def disp_button(obj,pos,mode = 1):

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

        x = screen_w - col_w/2 - o_w
        y = col_w/2 - o_h

    elif pos == 3:

        x = col_w/2 - o_w
        y = screen_h - col_w/2 - o_h

    else:

        x = screen_w - col_w/2 - o_w
        y = screen_h - col_w/2 - o_h

    screen.blit(obj,(x,y))
    
def disp_result(link):

        disp_time = result_disp_time
        start_time = time.clock()
        check = 0

        while True:

            if time.clock() - start_time >= disp_time:

                white_block = pygame.Surface((col_w, screen_h/2))
                white_block.fill(white)
                screen.blit(white_block,(screen_w-col_w,0))
                
                break
                            
            #Display numbers in upper right corner
            white_rect = pygame.Surface((100, 100))
            white_rect.fill(white)
            white_rect.fill(white, rect=None, special_flags=0)
            disp_button(white_rect,2)

            #Disp number
            disp_button(buttonfont.render(str(int(disp_time-(time.clock() - start_time)+1)), True, black),2)
            pygame.display.flip()

            #Check if upload wanted/show existing qr code

            if get_key() == 3 and mode == 1:

                disp_time = disp_time - time.clock() + start_time

                if check == 0:

                    check == 1
                    dropbox_link = dropbox_upload(link)
                    qr_code = create_qr_code(dropbox_link)

                disp_obj(qr_code,0)

                white_block = pygame.Surface((col_w, screen_h/2))
                white_block.fill(white)
                screen.blit(white_block,(0,0))

                disp_button(space,1)
                disp_button(lbl_return,1,2)

                pygame.display.flip()
                
                while True:
                    
                    if get_key() == 0:
                        break;

                img = pygame.image.load(link)
                disp_obj(img,0)
                screen.blit(white_block,(0,0))

                disp_button(up,1)
                disp_button(lbl_qr_code,1,2)

                start_time = time.clock()

        layout(1)

def layout(settings):

    screen.fill(white)

    if settings == 1:

        disp_button(space,1)
        disp_button(lbl_take_photo,1,2)
        disp_button(left,3)
        disp_button(lbl_previous,3,2)
        disp_button(right,4)
        disp_button(lbl_next,4,2)

    elif mode == 1:
    
        disp_button(up,1)
        disp_button(lbl_dropbox,1,2)
        
    pygame.display.flip()

#   Image processing/editing

def img_combine(img_1,img_2,img_3,img_4): #combines 4 images to one and returns the results

    x = screen_w/2 - col_w
    y = screen_h/2

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
    img_data = result.tostring()

    img_pg = pygame.image.fromstring(img_data,img_size,img_mode)
    
    return img_pg, img_link

#   Key detection/definition

def def_keys():

    wv = True
        
    while wv == True:
        event = pygame.event.wait()
        type_int = int(event.type)
        if type_int in [2,5]:
            types.extend([type_int])
            if type_int == 2:
                keys.extend([int(event.key)])
            else:
                keys.extend([int(event.button)])
            
            if len(types) >= num_keys:
                wv = False

    return keys, types

def key_type(event):

    for i in range(0,num_keys):
        if int(event.type) == 2:
            if keys[i] == int(event.key):
                return i
        if int(event.type) == 5:
            if keys[i] == int(event.button):
                return i

def get_key():

    for event in pygame.event.get():

        if int(event.type) in [2,5]:
                    
            check = key_type(event) #get last pressed key
            
            return check

#   Processes

def img_taking(): #Takes 4 images which are getting combined afterwards

    try:
        link = start_liveview()
    except:
        con = False
        while con == False:
            try:
                con == True
                post_method('startRecMode')
            except:
                print 'Connection problem'
                con == False

    #Take 4 images
       
    img_1 = countdown_img(link,1)
    time.sleep(1)
    img_2 = countdown_img(link,2)
    time.sleep(1)
    img_3 = countdown_img(link,3)
    time.sleep(1)
    img_4 = countdown_img(link,4)

    #Combine images

    disp_obj(lbl_wait)

    post_method('stopLiveview')

    img_result, img_link = img_combine(img_1,img_2,img_3,img_4)
    
    layout(2)
    disp_obj(img_result,0)

    pygame.event.clear()
    disp_result(img_link)

    pygame.event.clear()
    

def countdown_img(link,pos): #Gives countdown and takes image

    screen.fill(white)
    pygame.display.flip()

    a = time.clock() - 0.1

    bol = True

    while bol == True:

        b = time.clock()

        if ((a-b)*m+t) > 0:
        
            stream = urllib2.urlopen(link)
            
            data = stream.read(136)

            size = struct.unpack('>i','\x00'+data[12:15])[0]
            imgdata = stream.read(size)

            img_bytes = pygame.image.load(io.BytesIO(imgdata))

            disp_preview(img_bytes,pos)
            
            disp_obj(str(int((a-b)*m+t+1)),2)
        
        else:
            bol = False


    disp_obj(lbl_smile)
    
    img_link = take_picture()

    img_res = Image.open(io.BytesIO(urllib2.urlopen(img_link).read()))

    return img_res

def wait(): #displays results and waits for input

        layout(1)

        start_time = time.clock()
        j = 0
        img_num = len(os.listdir("results"))

        while True:
            
                now = time.clock()

                if now - start_time >= 3:
                    
                    start_time = time.clock()
                    if img_num >= 2:
                        img_num = img_num - 1
                    else:
                        img_num = len(os.listdir("results"))

                check = get_key()

                if check == 0:      #key 0 -> new collage
                    img_taking()
                        
                elif check == 1:    #key 1 -> show previous collage
                    start_time = time.clock()
                    if img_num >= 2:
                        img_num = img_num - 1
                    else:
                        img_num = len(os.listdir("results"))
                                
                elif check == 2:    #key 2 -> show next collage
                        
                    start_time = time.clock()
                    if img_num < len(os.listdir("results")):
                        img_num = img_num + 1
                    else:
                        img_num = 1

                if img_num >= 1:
                    img = pygame.image.load("results/result" + str(img_num) + ".jpg")
                    disp_obj(img,0)

#Program

#   Check camera connection

#   Dropbox connection/Mode

get_mode_return = get_mode(app_key, app_secret)

if get_mode_return['mode'] == 0:
    mode = 0
else:
    mode = 1
    client = get_mode_return['client']

pygame.init()

#Off-Code festlegen

off_code = [0,1,2,0,1,2]

#Screensize definieren

screen = pygame.display.set_mode((1200,700))
##screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

info = pygame.display.Info()
screen_w = info.current_w
screen_h = info.current_h

myfont = pygame.font.SysFont(None,200)
buttonfont = pygame.font.SysFont(None,60)

up = pygame.image.load('up.jpg')
down = pygame.image.load('down.jpg')
left = pygame.image.load('left.jpg')
right = pygame.image.load('right.jpg')
space = pygame.image.load('space.jpg')

disp_obj(lbl_choose_keys)

keys,types = def_keys()

disp_obj(lbl_go)

try:
    post_method('startRecMode')
except:
    pygame.quit()
    print 'Check camera connection'
    raise SystemExit

wait()

pygame.quit()