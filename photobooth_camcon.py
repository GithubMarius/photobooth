'''
Created on 16.12.2016

@author: Marius
'''

#Import libraries

import requests        #to communicate with the camera
import json            #to send json objects
from photobooth_settings import url

#   Camera communication

def post_method(method,par = []): #general post_method for communication with camera

    payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    requests.post(url, data=data)

def start_liveview(): #start camera liveview

    method = 'startLiveview'
    par = []

    payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    resp = requests.post(url, data=data)
    resp_js = resp.json()
    link = str(resp_js.get('result')[0])

    return link

def take_picture(): #take one image and receive it

    method = 'actTakePicture'
    par = []

    payload =  {'method': method, 'params': par, 'id': 1, 'version': '1.0'}
    data = json.dumps(payload)
    resp = requests.post(url, data=data)
    resp_js = resp.json()
    res_con = str(resp_js.get('result')[0][0])

    return res_con