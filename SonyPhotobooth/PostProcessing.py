'''
Created on 30.07.2017

@author: Marius
'''

import os
from SonyPhotobooth.Settings import orgfolder, resultsfinefolder, x_space_fine, y_space_fine
from PIL import Image

files = os.listdir(orgfolder)
n = len(files)

for i in range(1,n/4):
    
    img1 = Image.open(orgfolder + '/' + files[4*(i-1)])
    img2 = Image.open(orgfolder + '/' + files[4*(i-1)+1])
    img3 = Image.open(orgfolder + '/' + files[4*(i-1)+2])
    img4 = Image.open(orgfolder + '/' + files[4*(i-1)+3])

    #Calc size
    width = 2*img1.width+3*x_space_fine
    height = 2*img1.height+3*y_space_fine
    x_right = 1*img1.width+2*x_space_fine
    y_bottom = 1*img1.height+2*y_space_fine
    
    result = Image.new("RGB", (width, height), "white")

    result.paste(img1,(x_space_fine,y_space_fine))
    result.paste(img2,(x_right,y_space_fine))
    result.paste(img3,(x_space_fine,y_bottom))
    result.paste(img4,(x_right,y_bottom))
    
    result.save(resultsfinefolder + '/resultfine' + str(i) + '.jpg')