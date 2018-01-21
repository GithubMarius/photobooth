'''
Created on 16.12.2016

@author: Marius
'''

#Import libraries
import requests, json, struct        #to communicate with the camera, send json objects, structs
from pygame import image
import io
from PIL import Image
from urllib.request import urlopen
from SonyPhotobooth.Input import getKey

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
        
        while True:
            try:
                respReq = requests.post(self.url, data=data).json()
                self.connected = True
                try:
                    resp = respReq.get('result')[0]
                    break
                except:
                    return
            except:
                self.connected = False
                print('Coudln''t connect. Retry in 3s. Press Exit-Key to stop trying.')
                Clock = self.pygame.time.Clock()
                ticksStart = self.pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s))
                
                while self.pygame.time.get_ticks()-ticksStart<3000:
                    Clock.tick(30)
                    if (getKey(self.pygame,self.Ser,self.Keys,self.numKeys) == self.numKeys-1):
                        print('Exit-Key pressed.')
                        raise SystemExit
            
            print('Try reconnecting.')
            
        return str(resp)
    
    def startRecMode(self):
        
        print('Starting recording mode.')
        self.postMethod('startRecMode',[])
    
    def startLiveview(self): #start camera liveview
    
        print('Starting liveview.')
        self.link = self.postMethod('startLiveview',[])
    
    def takePhoto(self): #take one image and receive it
    
        method = 'actTakePicture'
        par = []
    
        payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
        data = json.dumps(payload)
        resp = requests.post(self.url, data=data).json()
        resCon = str(resp.get('result')[0][0]) #[0][0] instead of [0]
        
        byteRes = io.BytesIO(urlopen(resCon).read());
        photo = Image.open(byteRes)
    
        return photo
    
    def readImgBytes(self,stream):
    
        data = stream.read(136)
        size = struct.unpack('>i',b'\x00'+data[12:15])[0] #Take relevant bytes
        imgData = stream.read(size)
        pygameImg = image.load(io.BytesIO(imgData))
    
        return pygameImg