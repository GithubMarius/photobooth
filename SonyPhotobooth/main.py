'''
Created on 15.12.2016

@author: Marius
'''

def displayCheck():
    print('TO IMPLEMENT')
    ##TO IMPLEMENT
    
def initPhotobooth():
    
    Config = ConfigParser(interpolation=ExtendedInterpolation(),inline_comment_prefixes='#')
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
    
    Info = pygame.display.Info() #Contains screen-size information
    
    ExtScreen = calcScreen(ScreenTot,Config,Info)
    
    #Fill Background Color
    ExtScreen.fillbg()
    pygame.display.flip()
    
    return Config, Ser, ScreenTot, Info, ExtScreen

def getTasks():
    taskfile = codecs.open('tasks.txt', 'r', 'iso-8859-15')
    lines = list()
    for i in taskfile.readlines():
        lines.append(i.rstrip('\r\n'))
        return lines

if __name__ == "__main__":    
    
    numKeys = 5
    
    # Import of Modules
    
    from SonyPhotobooth.Settings            import white, red, myfontsmall, yellow
    from SonyPhotobooth.ImageProcessing     import countdownImg, imgCombine
    from SonyPhotobooth.CamCon              import SonyCamera
    from SonyPhotobooth.Disp                import dispObj, calcScreen, dispChart, dispImg
    from SonyPhotobooth.Input               import setKeys, getKey, resetInputDevices
    from SonyPhotobooth.Serial              import Serialrep
    from configparser                       import ConfigParser, ExtendedInterpolation
    
    import pygame, serial, time, ctypes, codecs, random, sys
    import json,requests         #@UnusedImport  to send json objects
    
    if (len(sys.argv) == 2):
        if (sys.argv[1]=='DisplayCheck'):
            displayCheck()
    
    #To stop windows from auto resizing
    Config, Ser, ScreenTot, Info, ExtScreen = initPhotobooth()

    # Load from Config    
    buttonholdOrg =     pygame.image.load(Config.get('Layout-Images','imgHold')).convert_alpha()
    buttonholdMask =    pygame.image.load(Config.get('Layout-Images','imgHoldMask')).convert_alpha()
    
    framerate =         Config.getfloat('General','framerate')
    tDisp =             Config.getfloat('General','tDisp')
    tSwipe =            Config.getfloat('General','tSwipe')
    tRand =             Config.getfloat('General','tRand')
    tMove =             Config.getfloat('General','tMove')
    tHold =             Config.getfloat('General','tHold')
    
    #Colors    
    backgroundColor = [int(v.strip()) for v in Config.get('Layout-Colors','backgroundColor').split(',')]
    foregroundColor = [int(v.strip()) for v in Config.get('Layout-Colors','foregroundColor').split(',')]
    
    # Load from Config end
        
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
    
    imgNum =        0
    ticksMoveSt1 =  0
    ticksMoveSt2 =  0
    
    #Get Iso for externalFlash calibration
    if Config.get('Settings','externalFlash') == 1:
        takeIso =   Camera.postMethod('getIsoSpeedRate')    #Get Standard Iso 
        takeF =     Camera.postMethod('getFNumber')         #Get Standard F
        takeS =     Camera.postMethod('getShutterSpeed')    #Get Shutter Speed
    else:
        takeIso = [];
        takeF = [];
        takeS = [];
    
    #Wait  for Key press
    while True:
          
        #Limit framerate
        Clock.tick(framerate)
     
        #random 1
        x = random.randint(1,tRand*framerate)
        if x == tRand*framerate and ticksMoveSt1 == 0:
            ticksMoveSt1 = pygame.time.get_ticks()
            ExtScreen.move_1 =  1
            ExtScreen.moved =   1
        elif pygame.time.get_ticks() >= ticksMoveSt1 + tMove*1000 and ticksMoveSt1 != 0:
            ticksMoveSt1 =      0
            ExtScreen.move_1 =  0
            ExtScreen.moved =   1
        else:
            ExtScreen.moved =   0
     
        #random 2
        x = random.randint(1,tRand*framerate)
        if x == tRand*framerate and ticksMoveSt2 == 0:
            ticksMoveSt2 = pygame.time.get_ticks()
            ExtScreen.move_2 =  1
            ExtScreen.moved =   1
        elif pygame.time.get_ticks() >= ticksMoveSt2 + tMove*1000 and ticksMoveSt2 != 0:
            ticksMoveSt2 =      0
            ExtScreen.move_2 =  0
            ExtScreen.moved =   1
        else:
            ExtScreen.moved =   0
         
        #Get pressed key
        i = getKey(pygame,Ser,Keys,numKeys)
         
        ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
                 
        if dispChart(ExtScreen,ticksStart,ticks_en,tSwipe): #returns True if time reached
            ticksStart = pygame.time.get_ticks()
            imgNum -= 1
            imgNum = dispImg(ExtScreen,imgNum)
     
        #Take new image
        if i == 0:
             
            buttonhold = buttonholdOrg.copy()
        
            time.sleep(0.3)
            
            tick_st = pygame.time.get_ticks()
            
            TransSurf = pygame.Surface((ExtScreen.width,ExtScreen.height), pygame.SRCALPHA) #@UndefinedVariable
            TransSurf.fill((0,0,0,128))
            
            showHoldButton = 0
            
            while Keys[0].checkHold(pygame,Ser):
                 
                percent = float(pygame.time.get_ticks() - tick_st)/(tHold*1000)
                
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
            link = Camera.startLiveview()
                            
            #TODO PACK IN FOR LOOP
            ExtScreen.fillbg()
            pygame.display.flip()
                             
            img1 = countdownImg(ExtScreen,Camera,Config,Ser,link,Clock,1,takeIso,takeF,takeS)
            #------------------------------------ img1 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
                       
            #time.sleep(2)           
                        
            img2 = countdownImg(ExtScreen,Camera,Config,Ser,link,Clock,2,takeIso,takeF,takeS)
            #------------------------------------ img2 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
             
            img3 = countdownImg(ExtScreen,Camera,Config,Ser,link,Clock,3,takeIso,takeF,takeS)
            #------------------------------------ img3 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
             
            img4 = countdownImg(ExtScreen,Camera,Config,Ser,link,Clock,4,takeIso,takeF,takeS)
            #------------------------------------ img4 = Image.open('img/test.jpg')
            ExtScreen.fillbg()
            pygame.display.flip()
             
            img_result, img_link = imgCombine(ExtScreen,img1,img2,img3,img4)
             
            ExtScreen.dispMode(0,1)
             
            dispObj(img_result,ExtScreen,white,0)
             
            ticksStart = pygame.time.get_ticks()  #ticks for moment of start (=ms)/(1000ms/s)
             
            while True:
                #Limit framerate
                Clock.tick(framerate)
     
                ticks_en = pygame.time.get_ticks() #ticks for moment of start (=ms)/(1000ms/s)
                 
                if dispChart(ExtScreen,ticksStart,ticks_en,tDisp): #returns True if time reached
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