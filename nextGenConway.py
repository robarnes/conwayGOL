#!/usr/bin/python
# class turorial : https://www.tutorialspoint.com/python/python_classes_objects.htm
# graphics tutorial : http://anh.cs.luc.edu/python/hands-on/3.1/handsonHtml/graphics.html

try:
    from graphics import *  #otherwise we are probably coding on the pc
except:
  print("Graphics library doesn't exist")
else:
  neoPixel          = False #set a variable we can check later

try: 
    from rpi_ws281x import *  #lets see if we can get neopixel (tells us we are on the raspberryPi)
except:
  print("Neopixel library doesn't exist")
else:
    neoPixel        = True   #set a variable we can check later
    LED_COUNT      = 2304     # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
    LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    STRIP_TYPE     = rpi_ws281x.ws.WS2811_STRIP_GRB

import argparse
import signal
import sys
import time
import random
import paho.mqtt.client as mqtt

#setting up MQTT
broker_url = "mqtt.widgetninja.net"
broker_port = 1883

def on_connect(client, userdata, flags, rc):
   #print("Connected With Result Code: {}".format(rc))
   client.subscribe("gameOfLife/reset")

def on_message(client, userdata, message):
    global mqttReset
    #print("message received " ,str(message.payload.decode("utf-8")))
    #rint("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    if (str(message.payload.decode("utf-8")) == "reset"): # did we get an MQTT message to reset?
        mqttReset = 1

def on_log(client, userdata, level, buf):
    print("log: ",buf)

client = mqtt.Client("GameOfLife")
client.username_pw_set(username="anonymous",password="anonymous")

try:
    client.connect(broker_url, broker_port)
except:
    print("MQTT Connection failed")

client.on_connect = on_connect
client.on_message = on_message
#client.on_log=on_log

client.loop_start()
#client.loop_forever()

numOfColumns = 68 #what can we see on your display
numOfRows = 68    #what can we see on your display
cellCount = 0     #used to track cell counts between rounds.  Used to catch 'stable' configurations
stableCycleCount = 0 #used to track how many rounds the cell count has been stable/stagnant
mqttReset = 0     #used to call world reset via MQTT

current_milli_time = int(round(time.time() * 1000))  #these are used to update display at pre-ordained intervals
last_milli_time = int(round(time.time() * 1000))
updateRate = 1000 #how often do we update display (in milliseconds)

class Cell:
    'Common base class for all cells'
 
    def __init__(self,col,row):
        self.location = [col, row]
        self.genes = "xx"
        self.age = 0
        self.alive = 0
        self.aliveFuture = 0
        self.matrixLocation = 0

    def setLocation(self,location):
        self.matrixLocation = location

    def kill(self):
        self.aliveFuture = 0
    
    def resurrect(self):
        self.aliveFuture = 1
        self.age = 0

    def setGenes(self,genes):
        self.genes = genes

    def birthday(self):
        self.age = self.age + 1

    def nextRound(self):
        self.alive = self.aliveFuture

def generateSeeds(world):
    time.sleep(5)  # lets pause and reflect before we reset the world

    # lets seed the world with about 20%
    numberOfSeeds = int((numOfColumns*numOfRows)*.2)
    for x in range(numberOfSeeds):
        seedRow = random.randint(0, numOfRows-1)
        seedCol = random.randint(0, numOfColumns-1)
        geneticOutcome = random.randint(0, 2)
        if geneticOutcome == 0:
            world[seedRow][seedCol].setGenes("PP")  # Team Purple!
        elif geneticOutcome == 1:
            world[seedRow][seedCol].setGenes("GG")  # Team Green!
        elif geneticOutcome == 2:
            world[seedRow][seedCol].setGenes("oo")  # Team Orange!
        world[seedRow][seedCol].alive = 1 #make the cell alive
    return world

def createWorld():
    world = [[Cell(i, j) for i in range(numOfColumns)] for j in range(numOfRows)]  # create the world
    return world

def checkDiversity(world, numOfRows, numOfColumns):
    purpleCount = 0
    greenCount = 0
    blueCount = 0
    orangeCount = 0
    purpleOrangeCount = 0
    greenOrangeCount = 0
    for rowNumber in range(numOfRows):
        for colNumber in range(numOfColumns):
            if world[rowNumber][colNumber].alive: #only count genes if cell is alive
                if world[rowNumber][colNumber].genes == 'PP':
                    purpleCount = 1
                elif world[rowNumber][colNumber].genes == 'GG':
                    greenCount = 1
                elif world[rowNumber][colNumber].genes == 'PG':
                    blueCount = 1
                elif world[rowNumber][colNumber].genes == 'oo':
                    orangeCount = 1
                elif world[rowNumber][colNumber].genes == 'Po':
                    purpleOrangeCount = 1
                elif world[rowNumber][colNumber].genes == 'Go':
                    greenOrangeCount = 1
    if purpleCount + greenCount + blueCount + orangeCount + purpleOrangeCount + greenOrangeCount > 1:
        return True #there is genetic diversity
    elif purpleCount + greenCount + blueCount + orangeCount + purpleOrangeCount + greenOrangeCount < 1:
        return False #everyone is dead
    else:
        return False #there is no longer genetic diversity

def in_bounds(rowNumber, colNumber):
    global numOfColumns
    global numOfRows
    if rowNumber < 0 or colNumber < 0:
        return False
    if rowNumber > (numOfColumns-1) or colNumber > (numOfRows-1):
        return False
    return True

def neighbors(world, rowNumber, colNumber):
    numNeighbors = 0
    for rowShift in range(-1,2,1):
        for colShift in range(-1,2,1):
            if in_bounds(rowNumber+rowShift, colNumber+colShift): #lets not be checking off the map..
                if world[rowNumber+rowShift][colNumber+colShift].alive: #this a living neighbor?
                    numNeighbors = numNeighbors + 1
    if world[rowNumber][colNumber].alive:  #lets not count ourselves, ok?
        numNeighbors = numNeighbors - 1
    return numNeighbors

def newCell(world, rowNumber, colNumber):
    potentialParents = [] #initialize array to store potential parents
    for rowShift in range(-1,2,1): #here we are looking at the neighbors
        for colShift in range(-1,2,1):
            if in_bounds(rowNumber+rowShift, colNumber+colShift):
                if world[rowNumber+rowShift][colNumber+colShift].alive: #if neighbor is alive, grab their genetics
                    potentialParents.append(world[rowNumber+rowShift][colNumber+colShift].genes)  #add this as a potential new parent
    #print(potentialParents)
    parentOneIndex = random.randint(0,len(potentialParents)-1) #randomly choose one
    parentOne = potentialParents[parentOneIndex] #lock it in
    potentialParents.pop(parentOneIndex) #remove from list of potential parents
    parentTwoIndex = random.randint(0,len(potentialParents)-1) #randomly choose one
    parentTwo = potentialParents[parentTwoIndex] #lock it in

    if (parentOne=='PP' and parentTwo=='PP'): #PP meet PP
        return('PP')
    elif (parentOne=='GG' and parentTwo=='GG'): #GG meet GG
        return('GG')
    elif (parentOne=='PP' and parentTwo=='GG'): #PP meet GG
        return('PG')
    elif (parentOne=='GG' and parentTwo=='PP'): #GG meet PP
        return('PG')   
    elif (parentOne=='PG' and parentTwo=='PG'): #PG meet PG
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('GG')
        elif geneticOutcome == 2 or geneticOutcome == 3:
            return('PG')
    elif (parentOne=='PP' and parentTwo=='PG'): #PP meet PG
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('PG')
    elif (parentOne=='PP' and parentTwo=='oo'): #PP meet oo
        return('Po')
    elif (parentOne=='PP' and parentTwo=='Po'): #PP meet Po
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('Po')
    elif (parentOne=='PP' and parentTwo=='Go'): #PP meet Go
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Po')
    elif (parentOne=='GG' and parentTwo=='PG'): #GG meet PG
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('GG')
    elif (parentOne=='GG' and parentTwo=='oo'): #GG meet oo
        return('Go')
    elif (parentOne=='GG' and parentTwo=='Po'): #GG meet Po
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
    elif (parentOne=='GG' and parentTwo=='Po'): #GG meet Po
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
    elif (parentOne=='GG' and parentTwo=='Go'): #GG meet Go
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('GG')
        elif geneticOutcome == 1:
            return('Go')
    elif (parentOne=='PG' and parentTwo=='oo'): #PG meet oo
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('Go')
    elif (parentOne=='PG' and parentTwo=='Po'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('PG')
        elif geneticOutcome == 2:
            return('Po')
        elif geneticOutcome == 3:
            return('Go')
    elif (parentOne=='PG' and parentTwo=='Go'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('GG')
        elif geneticOutcome == 1:
            return('PG')
        elif geneticOutcome == 2:
            return('Po')
        elif geneticOutcome == 3:
            return('Go')
    elif (parentOne=='PG' and parentTwo=='PP'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('PG')
    elif (parentOne=='PG' and parentTwo=='GG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('GG')
    elif (parentOne=='oo' and parentTwo=='oo'):
        return('oo')
    elif (parentOne=='oo' and parentTwo=='Po'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('oo')
    elif (parentOne=='oo' and parentTwo=='Go'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Go')
        elif geneticOutcome == 1:
            return('oo')
    elif (parentOne=='oo' and parentTwo=='PP'):
        return('Po')
    elif (parentOne=='oo' and parentTwo=='GG'):
        return('Go')
    elif (parentOne=='oo' and parentTwo=='PG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('Go')
    elif (parentOne=='Po' and parentTwo=='Po'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('oo')
        elif geneticOutcome == 2 or geneticOutcome == 3:
            return('Po')
    elif (parentOne=='Po' and parentTwo=='Go'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
        elif geneticOutcome == 2:
            return('Po')
        elif geneticOutcome == 3:
            return('oo')
    elif (parentOne=='Po' and parentTwo=='PP'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('Po')
    elif (parentOne=='Po' and parentTwo=='GG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
    elif (parentOne=='Po' and parentTwo=='PG'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('Po')
        elif geneticOutcome == 2:
            return('PG')
        elif geneticOutcome == 3:
            return('Go')
    elif (parentOne=='Po' and parentTwo=='oo'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('oo')
    elif (parentOne=='Go' and parentTwo=='Go'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('GG')
        elif geneticOutcome == 1:
            return('oo')
        elif geneticOutcome == 2 or geneticOutcome == 3:
            return('Go')
    elif (parentOne=='Go' and parentTwo=='PP'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('PG')
    elif (parentOne=='Go' and parentTwo=='GG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Go')
        elif geneticOutcome == 1:
            return('GG')
    elif (parentOne=='Go' and parentTwo=='PG'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Po')
        elif geneticOutcome == 2:
            return('GG')
        elif geneticOutcome == 3:
            return('Go')
    elif (parentOne=='Go' and parentTwo=='oo'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Go')
        elif geneticOutcome == 1:
            return('oo')
    elif (parentOne=='Go' and parentTwo=='Po'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Po')
        elif geneticOutcome == 2:
            return('Go')
        elif geneticOutcome == 3:
            return('oo')
    else:
        print('for some reason we are using fallback gene')
        return('GG') #fallback gene?

def checkLife(world, rowNumber, colNumber):
    if world[rowNumber][colNumber].alive == 0: #no need to spawn life if already alive
        if neighbors(world, rowNumber, colNumber) == 3: #does this cell have three neighbors?
            world[rowNumber][colNumber].setGenes(newCell(world,rowNumber,colNumber)) #find our parents/genetics
            world[rowNumber][colNumber].resurrect() #flag to be alive in the next cycle
            #print("birthed cell genes:", cellFuture[rowNumber][colNumber]) #new cell with genes from 'parents'
    else: #if alive, see if stays alive    
        if neighbors(world, rowNumber, colNumber) < 2: #do you have less than two neighbors?
            world[rowNumber][colNumber].kill() #sorry, you die
        elif neighbors(world, rowNumber, colNumber) > 3: #do you have more than 3 neighbors?
            world[rowNumber][colNumber].kill() #sorry, you die
    return world

def checkStable(world, numOfRows, numOfColumns, lastCellCount, stableCycleCount):
    cellCount = 0
    for rowNumber in range(numOfRows):
        for colNumber in range(numOfColumns):
            cellCount = cellCount + world[rowNumber][colNumber].alive #add one to the counter if alive
    if lastCellCount == cellCount:  #likely all stable formations
        stableCycleCount = stableCycleCount + 1
    elif (lastCellCount + 4 == cellCount) or (lastCellCount + 8 == cellCount) or (lastCellCount - 12 == cellCount): # likly pulsar formations
        stableCycleCount = stableCycleCount + 1
    else:
        stableCycleCount = 0
    return cellCount, stableCycleCount

def nextRound(world, numOfRows, numOfColumns):
    for rowNumber in range(numOfRows):
        for colNumber in range(numOfColumns):
            world[rowNumber][colNumber].nextRound()
    return world

def runSimulation(world, numOfRows,numOfColumns):
    for rowNumber in range(numOfRows):
        for colNumber in range(numOfColumns):
            world = checkLife(world, rowNumber, colNumber) #see if this cell is going to live or die
            if world[rowNumber][colNumber].alive:
                world[rowNumber][colNumber].birthday() #if alive, age a year
    return world

def draw(world, numOfRows, numOfColumns, win):
    #this function used for testing, drawing on screen instead of NEOPIXEL display
    for item in win.items[:]:
        item.undraw()
    win.update()
    for rowNumber in range(10,numOfRows-10): # we are chopping 10 rows/cols off the world.  Life 'offscreen' makes simulation look better
        for colNumber in range(10,numOfColumns-10):
            if world[rowNumber][colNumber].alive:
                dot = Circle(Point((rowNumber*8)+4, (colNumber*8)+4),4)
                if world[rowNumber][colNumber].genes == 'PP':
                    dot.setFill("purple")
                elif world[rowNumber][colNumber].genes == 'GG':
                    dot.setFill("green")
                elif world[rowNumber][colNumber].genes == 'PG':
                    dot.setFill("blue")
                elif world[rowNumber][colNumber].genes == 'oo':
                    dot.setFill("orange")
                elif world[rowNumber][colNumber].genes == 'Po':
                    dot.setFill("purple")
                elif world[rowNumber][colNumber].genes == 'Go':
                    dot.setFill("green")
                else:
                    print("missing somee important genetic info in draw()")
                    dot.setFill("yellow")
                dot.draw(win) # remove this line if you enable the ELSE below
            #else:
                #dot = Circle(Point((rowNumber*8)+4, (colNumber*8)+4),4)
                #dot.setFill("white")
            #dot.draw(win)

def drawNeoPixel(world, numOfRows, numOfColumns):
    for rowNumber in range(10,numOfRows-10):
        for colNumber in range(10,numOfColumns-10):
            if world[rowNumber][colNumber].alive:
                if world[rowNumber][colNumber].genes == 'PP':
                    strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(128,0,128)) #if alive set purple using the cell to rgb pixel map 
                elif world[rowNumber][colNumber].genes == 'GG':
                    strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(0,128,0)) #if alive set green using the cell to rgb pixel map
                elif world[rowNumber][colNumber].genes == 'PG':
                    strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(0,0,128)) #if alive set blue using the cell to rgb pixel map 
                elif world[rowNumber][colNumber].genes == 'oo':
                    strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(128,80,0)) #if alive set orange using the cell to rgb pixel map 
                elif world[rowNumber][colNumber].genes == 'Po':
                    strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(128,0,128)) #if alive set purple using the cell to rgb pixel map
                elif world[rowNumber][colNumber].genes == 'Go':
                    strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(0,128,0)) #if alive set green using the cell to rgb pixel map 
                else:
                    print("missing some important genetic info in drawNeoPixel()")
            else:
                strip.setPixelColor(world[rowNumber][colNumber].matrixLocation,Color(0,0,0))      #if dead turn off
    strip.show()

def rgbLedMapping(world):
    location = 0
    colNumber = 0
    # all the +10 shennanigans are an offset so part of the simulation is 'offscreen'
    while colNumber < 48: #top 3 16x16 rgb panels
        for rowNumber in range(0,16):
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber+10][colNumber+10].setLocation(location)
            location += 1
        colNumber += 1
        if colNumber <= 47: #don't overrun the matrix
            for rowNumber in range(15,-1,-1):
                #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
                world[rowNumber+10][colNumber+10].setLocation(location)
                location += 1
            colNumber += 1
 
    colNumber = 32
    while colNumber < 48: #middle row, right 16x16 panel
        for rowNumber in range(16,32):
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber+10][colNumber+10].setLocation(location)
            location += 1
        colNumber += 1
        if colNumber <= 47: #don't overrun the matrix
            for rowNumber in range(31,15,-1):
                #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
                world[rowNumber+10][colNumber+10].setLocation(location)
                location += 1
            colNumber += 1
 
    colNumber = 16
    while colNumber < 32: #middle row, right 16x16 panel
        for rowNumber in range(16,32):
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber+10][colNumber+10].setLocation(location)
            location += 1
        colNumber += 1
        if colNumber <= 47: #don't overrun the matrix
            for rowNumber in range(31,15,-1):
                #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
                world[rowNumber+10][colNumber+10].setLocation(location)
                location += 1
            colNumber += 1

    colNumber = 0
    while colNumber < 16: #middle row, left 16x16 panel
        for rowNumber in range(16,32):
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber+10][colNumber+10].setLocation(location)
            location += 1
        colNumber += 1
        if colNumber <= 47: #don't overrun the matrix
            for rowNumber in range(31,15,-1):
                #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
                world[rowNumber+10][colNumber+10].setLocation(location)
                location += 1
            colNumber += 1

    colNumber = 0
    while colNumber < 48:  #bottom 3 16x16 rgb panels
        for rowNumber in range(32,48):
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber+10][colNumber+10].setLocation(location)
            location += 1
        colNumber += 1
        if colNumber <= 47: #don't overrun the matrix
            for rowNumber in range(47,31,-1):
                #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
                world[rowNumber+10][colNumber+10].setLocation(location)
                location += 1
            colNumber += 1
    return world

if neoPixel:
    #setup NeoPixels
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, STRIP_TYPE)
    strip.begin()
else:
    win = GraphWin('planet', numOfRows*8, numOfColumns*8) # give title and dimensions of the graphical window/display

world = createWorld()
world = generateSeeds(world)
world = rgbLedMapping(world)

while True:
    world = runSimulation(world, numOfRows, numOfColumns) # see who lives, dies, who is born (but don't kill cells until we check all of them)
    world = nextRound(world, numOfRows, numOfColumns) # advance the cell status for next round (ie flag as born/dead)
    if neoPixel:
        drawNeoPixel(world, numOfRows, numOfColumns) # display the outcome on neopixel display
    else:
        draw(world, numOfRows, numOfColumns, win) # display the outcome using graphics library
    cellCount, stableCycleCount = checkStable(world, numOfRows, numOfColumns, cellCount, stableCycleCount)
    #print("CellCount: ", cellCount)
    if stableCycleCount > 20 : #world is boring / cyclic
        world = generateSeeds(world)
        stableCycleCount = 0
    elif checkDiversity(world, numOfRows, numOfColumns) == False: # if noone is alive, or only one color is alive, then restart
        world = generateSeeds(world)
        stableCycleCount = 0
    elif mqttReset == 1: #message via MQTT to reset
        world = generateSeeds(world)
        stableCycleCount = 0
        mqttReset = 0
    #publish some updates to MQTT
    #client.publish(topic="gameOfLife/cellCount", payload=cellCount, qos=0, retain=False)
    
    #manage the speed of the simulation
    current_milli_time = int(round(time.time() * 1000))  
    sleepTime = updateRate - (current_milli_time - last_milli_time)
    sleepTime = sleepTime * .001 #converting from millisconds to seconds for sleep function
    if (sleepTime < 0): #if we are behind schedule, don't sleep
        sleepTime = 0
    #print("Sleep time: ", sleepTime)
    time.sleep(sleepTime)
    last_milli_time = int(round(time.time() * 1000))