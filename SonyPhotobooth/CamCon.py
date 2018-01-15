'''
Created on 16.12.2016

@author: Marius
'''

#Import libraries

import requests        #to communicate with the camera
import json            #to send json objects
import struct
from pygame import image
import io
from PIL import Image
from urllib.request import urlopen #only on python 2.X running
from SonyPhotobooth.Input import getKey
#===============================================================================
# try:
#     from urllib2 import urlopen
# except ImportError:
#     from urllib.request import urlopen
#===============================================================================

class CameraConnectionError(Exception):
    pass

class SonyCamera():
    
    def __init__(self,url,pygame,Ser,Keys,numKeys):
        self.url = url
        self.pygame = pygame
        self.Ser = Ser
        self.Keys = Keys
        self.numKeys = numKeys
        self.connected = False
        self.recMode = False
        pass
    
    #Checks if reachable
    #def checkStatus(self):

    #   Camera communication
    def postMethod(self,method,par = []): #general postMethod for communication with camera
        
        payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
        data = json.dumps(payload)
        try:
            resp = requests.post(self.url, data=data)
            self.connected = True
        except:
            self.connected = False
            raise CameraConnectionError
            
                
        return resp
    
    def startRecMode(self):
        
        while not self.connected:
            try:
                print('Trying to start recording mode.')
                self.postMethod('startRecMode',[])
            except CameraConnectionError:
                print('Coudln''t connect. Retry in 3s. Press Exit-Key to stop trying.')
                Clock = self.pygame.time.Clock()
                ticksStart = self.pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s))
                
                while self.pygame.time.get_ticks()-ticksStart<3000:
                    Clock.tick(30)
                    if (getKey(self.pygame,self.Ser,self.Keys,self.numKeys) == 4):
                        print('Exit-Key pressed.')
                        raise SystemExit
                    
                    
    
    def startLiveview(self): #start camera liveview
    
        method = 'startLiveview'
        par = []
    
        payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
        data = json.dumps(payload)
        resp = requests.post(self.url, data=data)
        resp_js = resp.json()
        link = str(resp_js.get('result')[0])
    
        return link
    
    def takePhoto(self): #take one image and receive it
    
        method = 'actTakePicture'
        par = []
    
        payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
        data = json.dumps(payload)
        resp = requests.post(self.url, data=data)
        resp_js = resp.json()
        res_con = str(resp_js.get('result')[0][0])
        
        byteRes = io.BytesIO(urlopen(res_con).read());
        photo = Image.open(byteRes)
    
        return photo
    
    def readImgBytes(self,stream):
    
        data = stream.read(136)
        size = struct.unpack('>i',b'\x00'+data[12:15])[0]
        imgData = stream.read(size)
        pygameImg = image.load(io.BytesIO(imgData))
    
        return pygameImg