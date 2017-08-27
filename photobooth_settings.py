'''
Created on 15.12.2016

@author: Marius
    '''

# Pygame Import

import pygame        #displaying contents on screen

pygame.font.init()

# Dimensions

col_w = 120

x_space = 30
y_space = 30

x_space_fine = 160
y_space_fine = 160

# Framerate
framerate = 30 #30

# Camera

url = 'http://192.168.122.1:8080/sony/camera'

preview_w = 640
preview_h = 424

# Colors

yellow =    pygame.Color(0,128,0)
black =     pygame.Color(0,0,0)
white =     pygame.Color(255,255,255)
red =       pygame.Color(255,0,0)

# Port for serial
COM = 'COM3'

# Time

m = 1                   #1.5 #adjust to get rid of delays
t = 4                   #countdown time
t_disp = 10              #image display time
t_swipe = 3             #image display time while displaying the images
t_hold = 3              #time to hold button for special task
t_cor = 0.3             #camera trigger correction time 

# For adjusted design
t_rand = 15             #time until random movement of person (adjusted design)
t_move = 1

# Image displaying

# Number of needed keys

num_keys = 4;

# Fonts

myfont =        pygame.font.SysFont(None,200)
buttonfont =    pygame.font.SysFont(None,60)
myfontsmall =   pygame.font.SysFont(None,80)

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

# Button images

up = pygame.image.load('img/up.png')
down = pygame.image.load('img/down.png')
left = pygame.image.load('img/left.png')
right = pygame.image.load('img/right.png')
space = pygame.image.load('img/space.png')

# Folder width resulting images

resultsfolder = 'results'
orgfolder = 'org'
resultsfinefolder = 'resultsfine'