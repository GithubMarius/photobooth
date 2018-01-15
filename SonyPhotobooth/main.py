'''
Created on 15.12.2016

@author: Marius
'''

def displayCheck():
    print('hi')
    
def initPhotobooth():
    
    Config = ConfigParser(interpolation=ExtendedInterpolation())
    Config.read('config.ini')
    
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    
    #Random
    random.seed()    
    
    #Check whether Serial connection is on port
    try:
        Ser = serial.Serial(
            port=Config.get('ExternalTrigger','COM'),
            baudrate=9600,
            timeout=0.01,
        )
    except:
        Ser = Serialrep()
    
    #Start pygame screen
    if (Config.get('Settings','fullScreen') == 1):
        ScreenTot = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    else:
        ScreenTot = pygame.display.set_mode((800,450),pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)
    
    buttonholdOrg =        pygame.image.load(Config.get('Layout-Images','imgHold')).convert_alpha()
    buttonholdMask =       pygame.image.load(Config.get('Layout-Images','imgHoldMask')).convert_alpha()
    
    Info = pygame.display.Info() #Contains screen-size information
    
    ExtScreen = calcScreen(ScreenTot,Info)
    
    #Fill Background Color
    ExtScreen.fillbg()
    pygame.display.flip()
    
    return Config, Ser, ScreenTot, buttonholdOrg, buttonholdMask, Info, ExtScreen

def getTasks():
    taskfile = codecs.open('tasks.txt', 'r', 'iso-8859-15')
    lines = list()
    for i in taskfile.readlines():
        lines.append(i.rstrip('\r\n'))
        return lines

if __name__ == "__main__":
      
    numKeys = 5
    
    # Import of Modules
    
    import pygame        #displaying contents on screen 
    from SonyPhotobooth.Settings            import white, red, framerate, t_disp, t_swipe, t_rand, t_move, t_hold, myfontsmall, yellow
    from SonyPhotobooth.ImageProcessing     import countdownImg, imgCombine
    from SonyPhotobooth.CamCon              import SonyCamera
    from SonyPhotobooth.Disp                import dispObj, calcScreen, dispChart, dispImg
    from SonyPhotobooth.Input               import setKeys, getKey, resetInputDevices
    from SonyPhotobooth.Serial              import Serialrep
    from configparser import ConfigParser, ExtendedInterpolation
    import serial, time, ctypes, codecs, random, sys
    import json,requests         #@UnusedImport  to send json objects
    
    if (len(sys.argv) == 2):
        if (sys.argv[1]=='DisplayCheck'):
            displayCheck()
    
    #To stop windows from auto resizing
    Config, Ser, ScreenTot, buttonholdOrg, buttonholdMask, Info, ExtScreen = initPhotobooth()
    
    Keys = setKeys(pygame,Ser,numKeys) # Let user assign keys
    
    Camera = SonyCamera(Config.get('General','url'),pygame,Ser,Keys,numKeys)
        
    dispObj(Config.get('Layout-Labels','lblChooseKeys'),ExtScreen,white)
    
    #---------------------------------------------------------- #Connect with camera
    Camera.startRecMode()
    
    #Read Tasks
    if Config.get('Settings','taskMode'): lines = getTasks();
        
    
    #Saves objects for the wished number of Keys
    
    #Initialize Clock
    Clock = pygame.time.Clock()
    ticksStart = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s))
    
    imgNum = 0
    ticksMoveSt1 = 0
    ticksMoveSt2 = 0
    
    #Get Iso for externalFlash calibration
    #if externalFlash == 1:
    
    #Get Standard Iso            
    resp = Camera.postMethod('getIsoSpeedRate')   
    respJs = resp.json()
    takeIso = str(respJs.get('result')[0])
    
    #Get Standard F            
    resp = Camera.postMethod('getFNumber')   
    respJs = resp.json()
    takeF = str(respJs.get('result')[0])
    
    #Get Shutter Speed            
    resp = Camera.postMethod('getShutterSpeed')   
    respJs = resp.json()
    takeS = str(respJs.get('result')[0])
 
    #Wait  for Key press
    while True:
          
        #Limit framerate
        Clock.tick(framerate)
     
        #random 1
        x = random.randint(1,t_rand*framerate)
        if x == t_rand*framerate and ticksMoveSt1 == 0:
            ticksMoveSt1 = pygame.time.get_ticks()
            ExtScreen.move_1 = 1
            ExtScreen.moved = 1
        elif pygame.time.get_ticks() >= ticksMoveSt1 + t_move*1000 and ticksMoveSt1 != 0:
            ticksMoveSt1 = 0
            ExtScreen.move_1 = 0
            ExtScreen.moved = 1
        else:
            ExtScreen.moved = 0
     
        #random 2
        x = random.randint(1,t_rand*framerate)
        if x == t_rand*framerate and ticksMoveSt2 == 0:
            ticksMoveSt2 = pygame.time.get_ticks()
            ExtScreen.move_2 = 1
            ExtScreen.moved = 1
        elif pygame.time.get_ticks() >= ticksMoveSt2 + t_move*1000 and ticksMoveSt2 != 0:
            ticksMoveSt2 = 0
            ExtScreen.move_2 = 0
            ExtScreen.moved = 1
        else:
            ExtScreen.moved = 0
         
        #Get pressed key
        i = getKey(pygame,Ser,Keys,numKeys)
         
        ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
                 
        if dispChart(ExtScreen,ticksStart,ticks_en,t_swipe): #returns True if time reached
            ticksStart = pygame.time.get_ticks()
            imgNum -= 1
            imgNum = dispImg(ExtScreen,imgNum)
     
        #Take new image
        if i == 0:
             
            buttonhold = buttonholdOrg.copy()
        
            time.sleep(0.3)
            
            tick_st = pygame.time.get_ticks()
            
            TransSurf = pygame.Surface((ExtScreen.width,ExtScreen.height), pygame.SRCALPHA) @UndefinedVariable
            TransSurf.fill((0,0,0,128))
            
            showHoldButton = 0
            
            while Keys[0].check_hold(pygame,Ser):
                 
                percent = float(pygame.time.get_ticks() - tick_st)/(t_hold*1000)
                 
                if percent >= 1:
                    dispObj(myfontsmall.render(lines[int(random.uniform(-0.5,len(lines)-0.501))], True, yellow),ExtScreen)
                    time.sleep(1)
                    break
                
                if percent >= 0.05:
                 
                    if showHoldButton == 0:
                        ExtScreen.blit(TransSurf)
                        pygame.display.flip()
                        showHoldButton = 1
                        
                    pygame.draw.rect(buttonhold,red,pygame.Rect(35,255-percent*165,330,percent*165))
                    buttonhold.blit(buttonholdMask,(35,90))
                    dispObj(buttonhold,ExtScreen,white,2)
                
                #Limit framerate
                Clock.tick(framerate)
                 
                pygame.event.get()
     
            #Try connecting to camera
            try:
                link = Camera.startLiveview()
            except:
                con = False
                while con == False:
                    try:
                        link = Camera.startLiveview()
                        con = True
                    except:
                        print('Connection problem')
                        con = False
                        
                        keyres = getKey(pygame,Ser,Keys,numKeys)
                        
                        if keyres == numKeys-1:
                            con = True
                            exit
                            
            ExtScreen.fillbg()
            pygame.display.flip()
                             
            img_1 = countdownImg(ExtScreen,Camera,Ser,link,Clock,1,takeIso,takeF,takeS)
            #------------------------------------ img_1 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
                       
            time.sleep(2)           
                        
            img_2 = countdownImg(ExtScreen,Camera,Ser,link,Clock,2,takeIso,takeF,takeS)
            #------------------------------------ img_2 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
             
            img_3 = countdownImg(ExtScreen,Camera,Ser,link,Clock,3,takeIso,takeF,takeS)
            #------------------------------------ img_3 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
             
            img_4 = countdownImg(ExtScreen,Camera,Ser,link,Clock,4,takeIso,takeF,takeS)
            #------------------------------------ img_4 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
             
            img_result, img_link = imgCombine(ExtScreen,img_1,img_2,img_3,img_4)
             
            ExtScreen.dispMode(0,1)
             
            dispObj(img_result,ExtScreen,white,0)
             
            ticksStart = pygame.time.get_ticks()  #ticks for moment of start (=ms)/(1000ms/s)
             
            while True:
                 
                #Limit framerate
                Clock.tick(framerate)
     
                ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
                 
                if dispChart(ExtScreen,ticksStart,ticks_en,t_disp): #returns True if time reached
                    break
                 
            resetInputDevices(pygame,Ser,Keys)
             
             
        elif i == 1:
    
            imgNum += 1
            ticksStart = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
             
            imgNum = dispImg(ExtScreen,imgNum)
             
        elif i == 2:
                 
            imgNum -= 1
            ticksStart = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
             
            imgNum = dispImg(ExtScreen,imgNum)
     
        elif i == numKeys-1:
            break
             
    #pygame.quit() #seems to be only in python 2.X needed