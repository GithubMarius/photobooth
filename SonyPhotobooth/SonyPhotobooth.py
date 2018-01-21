'''
Created on 15.12.2016

@author: Marius
'''
#Class with counters and changing variables

class varHolder:
    pass

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
    
    #State class for editable values, etc.
    State = varHolder()
    
    State.imgNum = 0;
    State.ticksMoveSt1 = 0;
    State.ticksMoveSt2 = 0;
    
    #Get Iso for externalFlash calibration
    if Config.get('Settings','externalFlash') == 1:
        State.takeIso =   Camera.postMethod('getIsoSpeedRate')    #Get Standard Iso 
        State.takeF =     Camera.postMethod('getFNumber')         #Get Standard F
        State.takeS =     Camera.postMethod('getShutterSpeed')    #Get Shutter Speed
    else:
        State.takeIso = [];
        State.takeF = [];
        State.takeS = [];
    
    #Settings class for settings values, etc.
    Settings = varHolder()
    Settings.framerate =         Config.getfloat('General','framerate')
    Settings.tDisp =             Config.getfloat('General','tDisp')
    Settings.tSwipe =            Config.getfloat('General','tSwipe')
    Settings.tRand =             Config.getfloat('General','tRand')
    Settings.tMove =             Config.getfloat('General','tMove')
    Settings.tHold =             Config.getfloat('General','tHold')
        
    #Read Tasks
    if Config.get('Settings','taskMode'): Settings.lines = getTasks();
        
    #Fill Background Color
    ExtScreen.fillbg()
    
    #Initialize pygame clock and add information
    Clock = ClockManager(Settings.framerate)
    
    return Config, State, Settings, Ser, ScreenTot, Info, ExtScreen, Clock

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
    from SonyPhotobooth.Input               import setKeys, getKey, resetInput
    from SonyPhotobooth.Serial              import Serialrep
    from SonyPhotobooth.ClockManager        import ClockManager
    from configparser                       import ConfigParser, ExtendedInterpolation
    
    import pygame, serial, time, ctypes, codecs, random, sys
    import json,requests         #@UnusedImport  to send json objects
    
    if (len(sys.argv) == 2):
        if (sys.argv[1]=='DisplayCheck'):
            displayCheck()
    
    #To stop windows from auto resizing
    Config, State, Settings, Ser, ScreenTot, Info, ExtScreen, Clock = initPhotobooth()

    # Load from Config    
    buttonholdOrg =     pygame.image.load(Config.get('Layout-Images','imgHold')).convert_alpha()
    buttonholdMask =    pygame.image.load(Config.get('Layout-Images','imgHoldMask')).convert_alpha()
    
    # Load from Config end
    Keys = setKeys(pygame,Ser,numKeys) # Let user assign keys
    
    Camera = SonyCamera(Config.get('General','url'),pygame,Ser,Keys,numKeys)
        
    dispObj(Config.get('Layout-Labels','lblChooseKeys'),ExtScreen,white)
    
    #---------------------------------------------------------- #Connect with camera
    Camera.startRecMode()
        
    #Saves objects for the wished number of Keys
    
    Clock.start()               #measure time from now (sets time in ms/1 ms = 1 tick)
    
    #Wait  for Key press
    while True:
        
        #Limit Settings.framerate
        Clock.tick()
        
        #TODO: Make Random Objects 
        
        #random 1
        x = random.randint(1,Settings.tRand*Settings.framerate)
        if x == Settings.tRand*Settings.framerate and State.ticksMoveSt1 == 0:
            State.ticksMoveSt1 = Clock.getT()
            ExtScreen.move_1 =      1
            ExtScreen.moved =       1
        elif Clock.getT() >= State.ticksMoveSt1 + Settings.tMove*1000 and State.ticksMoveSt1 != 0:
            State.ticksMoveSt1 =    0
            ExtScreen.move_1 =      0
            ExtScreen.moved =       1
        else:
            ExtScreen.moved =       0
     
        #random 2
        x = random.randint(1,Settings.tRand*Settings.framerate)
        if x == Settings.tRand*Settings.framerate and State.ticksMoveSt2 == 0:
            State.ticksMoveSt2 = Clock.getT()
            ExtScreen.move_2 =      1
            ExtScreen.moved =       1
        elif Clock.getT() >= State.ticksMoveSt2 + Settings.tMove*1000 and State.ticksMoveSt2 != 0:
            State.ticksMoveSt2 =    0
            ExtScreen.move_2 =      0
            ExtScreen.moved =       1
        else:
            ExtScreen.moved =       0
         
        #Get pressed key
        i = getKey(pygame,Ser,Keys,numKeys)
                 
        if dispChart(ExtScreen,Clock.ticksDiff(),Settings.tSwipe): #returns True if time reached
            Clock.start()
            State.imgNum -= 1
            State.imgNum = dispImg(ExtScreen,State.imgNum)
     
        #Take new image
        if i == 0:
             
            buttonhold = buttonholdOrg.copy()
        
            time.sleep(0.3)
            
            TransSurf = pygame.Surface((ExtScreen.width,ExtScreen.height), pygame.SRCALPHA) #@UndefinedVariable
            TransSurf.fill((0,0,0,128))
            
            Clock.start()
            
            showHoldButton = 0
            
            while Keys[0].checkHold(pygame,Ser):
                 
                percent = float(Clock.ticksDiff())/(Settings.tHold*1000) #note... percent not correct term. (1 = 100%, 0 = 0%... ratio is maybe better term)
                
                if percent >= 1:
                    dispObj(myfontsmall.render(Settings.lines[int(random.uniform(-0.5,len(Settings.lines)-0.501))], True, yellow),ExtScreen)
                    time.sleep(1)
                    break
                
                if percent >= 0.05:
                 
                    if showHoldButton == 0:
                        ExtScreen.blit(TransSurf)
                        ExtScreen.flip()
                        showHoldButton = 1
                        
                    pygame.draw.rect(buttonhold,red,pygame.Rect(35,255-percent*165,330,percent*165))
                    buttonhold.blit(buttonholdMask,(35,90))
                    dispObj(buttonhold,ExtScreen,white,2)
                
                #Limit framerate
                Clock.tick()
                pygame.event.get()
     
            #Try connecting to camera
            Camera.startLiveview()
                            
            ExtScreen.fillbg()
            
            Imgs = [None]*4
            
            for i in range(0,4):
                Imgs[i] = countdownImg(ExtScreen,Camera,Config,State,Ser,Clock,i+1)
                #------------------------------------ Imgs[i] = Image.open('img/test.jpg')
            
            Imgresult= imgCombine(ExtScreen,Imgs)
            
            ExtScreen.dispMode(0,1)
             
            dispObj(Imgresult,ExtScreen,white,0)
            
            Clock.start()  #ticks for moment of start (=ms)/(1000ms/s)
             
            while True:
                #Limit framerate
                Clock.tick()
                
                if dispChart(ExtScreen,Clock.ticksDiff(),Settings.tDisp): #returns True if time reached
                    break
                 
            resetInput(pygame,Ser,Keys)
             
             
        elif i == 1: #Show last picture (imgNum is inverted)
    
            State.imgNum += 1
            Clock.start() #ticks for moment of start (=ms)/(1000ms/s)
            State.imgNum = dispImg(ExtScreen,State.imgNum)
             
        elif i == 2: #Show next picture
                 
            State.imgNum -= 1
            Clock.start() #ticks for moment of start (=ms)/(1000ms/s)
            State.imgNum = dispImg(ExtScreen,State.imgNum)
     
        elif i == numKeys-1: #Last button => Exit
            print('Exit-Key pressed.')
            raise SystemExit

#if __name__ == "__screenInfo__":