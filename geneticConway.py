import numpy as np
import time
import random
from neopixel import *
import argparse
import signal
import sys

def signal_handler(signal, frame):
        colorWipe(strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 256     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

numOfColumns = 16 #what can we see on your display
numOfRows = 16    #what can we see on your display
unseenBorder = 10 #this border on all sides is processed, but not displayed.  tries to make world feel 'infinite'
numOfColumns = numOfColumns + (2*unseenBorder)
numOfRows = numOfRows + (2*unseenBorder)

current_milli_time = int(round(time.time() * 1000))  #these are used to update display at pre-ordained intervals
last_milli_time = int(round(time.time() * 1000))
updateRate = 1000 #how often do we update display (in milliseconds)
numberOfCycles = 0 #how long has this world been alive

purpleCount = 0
greenCount = 0
blueCount = 0
orangeCount = 0
purpleOrangeCount = 0
greenOrangeCount = 0

cellCurrent = [[0 for i in range(numOfColumns)] for j in range(numOfRows)]  #create an empty matrix for current state
cellFuture = [[0 for i in range(numOfColumns)] for j in range(numOfRows)]  #create an empty matrix for future state
cellDisplay = [[0 for i in range(numOfColumns-(2*unseenBorder))] for j in range(numOfRows-(2*unseenBorder))]  #create an empty matrix for the cells we will show
cellLifespan = [[0 for i in range(numOfColumns-(2*unseenBorder))] for j in range(numOfRows-(2*unseenBorder))]  #create an empty matrix for tracking lifespan
rgbMap = [[0 for i in range(numOfColumns-(2*unseenBorder))] for j in range(numOfRows-(2*unseenBorder))]  #create an empty matrix for mapping to how led's are numbered/ordered

staticWorldCount = 0 #this is used to see if world has become static / non-changing
staticWorldLastCellCount = 0 #used to count how many cycles the qty. of cells is static
staticWorldCurrentCellCount = 0

def clearSeedCount():
    global purpleCount
    global greenCount
    global blueCount
    global orangeCount
    global purpleOrangeCount
    global greenOrangeCount
    global staticWorldLastCellCount
    purpleCount = 0
    greenCount = 0
    blueCount = 0
    orangeCount = 0
    purpleOrangeCount = 0
    greenOrangeCount = 0
    staticWorldCurrentCellCount = 0

def generateSeeds():
    clearSeedCount()
    global numberOfCycles
    numberOfCycles = 0

    time.sleep(5) #little pause showing the end of the current world
    colorWipe(strip, Color(0,0,0)) #clear out all the led's

    numberOfSeeds = int((numOfColumns*numOfRows)*.1) #lets seed the world with about 10%
    for x in range(numberOfSeeds):
        seedRow = random.randint(0,numOfRows-1)
        seedCol = random.randint(0,numOfColumns-1)
        geneticOutcome = random.randint(0,2)
        if geneticOutcome == 0:
            cellCurrent[seedRow][seedCol] = 'PP' #Team Purple!
        elif geneticOutcome == 1:
            cellCurrent[seedRow][seedCol] = 'GG' #Team Green!
        elif geneticOutcome == 2:
            cellCurrent[seedRow][seedCol] = 'oo' #Team Orange!
        if unseenBorder < seedRow < numOfRows-(unseenBorder+1):
            if unseenBorder < seedCol < numOfColumns-(unseenBorder+1): #only show if in display area
                strip.setPixelColor(rgbMap[seedRow-unseenBorder][seedCol-unseenBorder],Color(255,128,64))      #lets show where new seeds landed!
    strip.show()
    time.sleep(5) #dramatic pause

def in_bounds(cellCurrent, row, col):
    if row < 0 or col < 0:
        return False
    if row > len(cellCurrent)-1 or col > len(cellCurrent)-1:
        return False
    return True

def neighbors(cellCurrent, rowNumber, colNumber):
    numNeighbors = 0
    for rowShift in range(-1,2,1):
        for colShift in range(-1,2,1):
            if in_bounds(cellCurrent, rowNumber+rowShift, colNumber+colShift):
                if cellCurrent[rowNumber+rowShift][colNumber+colShift] != 0:
                    numNeighbors = numNeighbors + 1
    if cellCurrent[rowNumber][colNumber] != 0:  #lets not count ourselves, ok?
        numNeighbors = numNeighbors - 1
    return numNeighbors

def newCell(cellCurrent, rowNumber, colNumber):
    potentialParents = [] #initialize array to store potential parents
    for rowShift in range(-1,2,1):
        for colShift in range(-1,2,1):
            if in_bounds(cellCurrent, rowNumber+rowShift, colNumber+colShift):
                if cellCurrent[rowNumber+rowShift][colNumber+colShift] != 0:
                    #print("parent could be: ", rowNumber+rowShift,colNumber+colShift)
                    potentialParents.append([rowNumber+rowShift,colNumber+colShift])  #add this as a potential new parent
    #print(potentialParents)
    parentOneIndex = random.randint(0,len(potentialParents)-1) #randomly choose one
    parentOne = potentialParents[parentOneIndex] #lock it in\
    potentialParents.pop(parentOneIndex) #remove from list of potential parents
    parentTwoIndex = random.randint(0,len(potentialParents)-1) #randomly choose one
    parentTwo = potentialParents[parentTwoIndex] #lock it in
    
    #print("Genes of parents:", cellCurrent[parentOne[0]][parentOne[1]], cellCurrent[parentTwo[0]][parentTwo[1]])
 
    if (cellCurrent[parentOne[0]][parentOne[1]]=='PP' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PP'): #PP meet PP
        return('PP')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='GG'): #GG meet GG
        return('GG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PP' and cellCurrent[parentTwo[0]][parentTwo[1]]=='GG'): #PP meet GG
        return('PG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PP'): #GG meet PP
        return('PG')   
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PG'): #PG meet PG
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('GG')
        elif geneticOutcome == 2 or geneticOutcome == 3:
            return('PG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PP' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PG'): #PP meet PG
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('PG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PP' and cellCurrent[parentTwo[0]][parentTwo[1]]=='oo'): #PP meet oo
        return('Po')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PP' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'): #PP meet Po
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('Po')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PP' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Go'): #PP meet Go
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Po')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PG'): #GG meet PG
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('GG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='oo'): #GG meet oo
        return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'): #GG meet Po
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'): #GG meet Po
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='GG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Go'): #GG meet Go
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('GG')
        elif geneticOutcome == 1:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='oo'): #PG meet oo
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('PG')
        elif geneticOutcome == 2:
            return('Po')
        elif geneticOutcome == 3:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Go'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('GG')
        elif geneticOutcome == 1:
            return('PG')
        elif geneticOutcome == 2:
            return('Po')
        elif geneticOutcome == 3:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PP'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('PG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='PG' and cellCurrent[parentTwo[0]][parentTwo[1]]=='GG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('GG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='oo' and cellCurrent[parentTwo[0]][parentTwo[1]]=='oo'):
        return('oo')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='oo' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('oo')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='oo' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Go'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Go')
        elif geneticOutcome == 1:
            return('oo')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='oo' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PP'):
        return('Po')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='oo' and cellCurrent[parentTwo[0]][parentTwo[1]]=='GG'):
        return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='oo' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Po' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('oo')
        elif geneticOutcome == 2 or geneticOutcome == 3:
            return('Po')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Po' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Go'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
        elif geneticOutcome == 2:
            return('Po')
        elif geneticOutcome == 3:
            return('oo')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Po' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PP'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('Po')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Po' and cellCurrent[parentTwo[0]][parentTwo[1]]=='GG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Po' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PG'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PP')
        elif geneticOutcome == 1:
            return('Po')
        elif geneticOutcome == 2:
            return('PG')
        elif geneticOutcome == 3:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Po' and cellCurrent[parentTwo[0]][parentTwo[1]]=='oo'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('oo')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Go' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Go'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('GG')
        elif geneticOutcome == 1:
            return('oo')
        elif geneticOutcome == 2 or geneticOutcome == 3:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Go' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PP'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Po')
        elif geneticOutcome == 1:
            return('PG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Go' and cellCurrent[parentTwo[0]][parentTwo[1]]=='GG'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Go')
        elif geneticOutcome == 1:
            return('GG')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Go' and cellCurrent[parentTwo[0]][parentTwo[1]]=='PG'):
        geneticOutcome = random.randint(0,3)
        if geneticOutcome == 0:
            return('PG')
        elif geneticOutcome == 1:
            return('Po')
        elif geneticOutcome == 2:
            return('GG')
        elif geneticOutcome == 3:
            return('Go')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Go' and cellCurrent[parentTwo[0]][parentTwo[1]]=='oo'):
        geneticOutcome = random.randint(0,1)
        if geneticOutcome == 0:
            return('Go')
        elif geneticOutcome == 1:
            return('oo')
    elif (cellCurrent[parentOne[0]][parentOne[1]]=='Go' and cellCurrent[parentTwo[0]][parentTwo[1]]=='Po'):
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

def checkLife(cellCurrent, rowNumber, colNumber):
    if cellCurrent[rowNumber][colNumber] == 0: #no need to spawn life if already alive
        if neighbors(cellCurrent, rowNumber, colNumber) == 3: #does this cell have three neighbors?
            newCell(cellCurrent, rowNumber, colNumber)
            cellFuture[rowNumber][colNumber] = newCell(cellCurrent, rowNumber, colNumber)
            #print("birthed cell genes:", cellFuture[rowNumber][colNumber]) #new cell with genes from 'parents'
    else: #if alive, see if stays alive    
        if neighbors(cellCurrent, rowNumber, colNumber) < 2: #do you have less than two neighbors?
            cellFuture[rowNumber][colNumber] = 0 #sorry, you die
        elif neighbors(cellCurrent, rowNumber, colNumber) > 3: #do you have more than 3 neighbors?
            cellFuture[rowNumber][colNumber] = 0 #sorry, you die

def geneticDiversityCount(cellCurrent, rowNumber, colNumber):
    global numberOfCycles
    global purpleCount
    global greenCount
    global blueCount
    global orangeCount
    global purpleOrangeCount
    global greenOrangeCount
    global staticWorldCurrentCellCount
    if cellCurrent[rowNumber][colNumber] == 'PP':
        purpleCount += 1
    elif cellCurrent[rowNumber][colNumber] == 'GG':
        greenCount += 1
    elif cellCurrent[rowNumber][colNumber] == 'PG':
        blueCount += 1
    elif cellCurrent[rowNumber][colNumber] == 'oo':
        orangeCount += 1
    elif cellCurrent[rowNumber][colNumber] == 'Po':
        purpleOrangeCount += 1
    elif cellCurrent[rowNumber][colNumber] == 'Go':
        greenOrangeCount += 1
    staticWorldCurrentCellCount = purpleCount + greenCount + blueCount + orangeCount + purpleOrangeCount + greenOrangeCount

def checkGeneticDiversity():
    global numberOfCycles
    global purpleCount
    global greenCount
    global blueCount
    global orangeCount
    global purpleOrangeCount
    global greenOrangeCount
    if purpleCount > 0 and greenCount + blueCount + orangeCount + purpleOrangeCount + greenOrangeCount == 0:
        return False
    elif greenCount > 0 and purpleCount + blueCount + orangeCount + purpleOrangeCount + greenOrangeCount == 0:
        return False
    elif blueCount > 0 and purpleCount + greenCount + orangeCount + purpleOrangeCount + greenOrangeCount == 0:
        return False
    elif orangeCount > 0 and purpleCount + greenCount + blueCount + purpleOrangeCount + greenOrangeCount == 0:
        return False
    elif purpleOrangeCount > 0 and purpleCount + greenCount + blueCount + orangeCount + greenOrangeCount == 0:
        return False
    elif greenOrangeCount > 0 and purpleCount + greenCount + blueCount + orangeCount + purpleOrangeCount == 0:
        return False
    else:
        return True
    
def runSimulation():
    global numberOfCycles
    clearSeedCount()
    for i in range(numOfRows):
        for j in range(numOfColumns):
            checkLife(cellCurrent, j, i)
            geneticDiversityCount(cellCurrent, j, i)

def worldTrim():
    for i in range(unseenBorder-1,numOfRows-unseenBorder, 1): #here we chop $unseenBorder rows/columns off each side of the world to make it look better
        for j in range(unseenBorder-1,numOfColumns-unseenBorder, 1):
            cellDisplay[i-unseenBorder][j-unseenBorder] = cellFuture[i][j]

def isWorldStatic():
    global staticWorldLastCellCount
    global staticWorldCurrentCellCount
    global staticWorldCount
    global numberOfCycles

    numberOfCycles += 1

    if staticWorldLastCellCount == staticWorldCurrentCellCount: #we have same number of cells as last time?
        staticWorldCount = staticWorldCount + 1 #how long has it been the same?
        #print('Static world count: %d' %(staticWorldCount))
    else:
        staticWorldCount = 0

    staticWorldLastCellCount = staticWorldCurrentCellCount

    if(numberOfCycles % 10 == 0): #only allow resets when stats are shown (every 10 turns)
        if staticWorldCurrentCellCount == 0 and staticWorldCount > 4: #everyone is dead, add seeds
            print("Reset: looks like they all died")
            staticWorldCount = 0
            return True
        elif staticWorldCount >= 120 and staticWorldCount > 4: #boooring.  add seeds
            print("Reset: world is boring")
            staticWorldCount = 0
            return True
        elif checkGeneticDiversity() == False:
            print("Reset: world is not diverse")
            staticWorldCount = 0
            return True
        else:
            return False #everything is cool
    else:
        return False #everything is cool

def checkLifespan():
    for i in range(numOfRows-(2*unseenBorder)):
        for j in range(numOfColumns-(2*unseenBorder)):
            if cellDisplay[i][j] == 1: #lets see if we are alive
                cellLifespan[i][j] = cellLifespan[i][j] + 1 #add to age
            else: #set age to zero
                cellLifespan[i][j] = 0

def displayWorld():
    #print(np.matrix(cellDisplay)) #show the world
    #print(np.matrix(rgbMap)) #show the world
    #print(np.matrix(cellLifespan)) #show how long each cell is alive
    #print(np.sum(cellDisplay))  #show total number of cells alive
    for i in range(0,numOfRows-(2*unseenBorder), 1):
        for j in range(0,numOfColumns-(2*unseenBorder), 1):
            if cellDisplay[i][j] != 0: #is the cell alive
#commenting out code to display cells based on lifespan                
#                if cellLifespan[i][j] > 60:
#                            strip.setPixelColor(rgbMap[i][j],Color(128,0,128)) #if alive set violet using the cell to rgb pixel map
#                elif cellLifespan[i][j] > 15:
#                            strip.setPixelColor(rgbMap[i][j],Color(128,0,0)) #if alive set red using the cell to rgb pixel map
#                elif cellLifespan[i][j] > 5:
#                            strip.setPixelColor(rgbMap[i][j],Color(128,128,0)) #if alive set yellow using the cell to rgb pixel map
#                else:
#                            strip.setPixelColor(rgbMap[i][j],Color(0,64,90)) #if alive set blue using the cell to rgb pixel map
                if cellDisplay[i][j] == 'PP':
                    strip.setPixelColor(rgbMap[i][j],Color(128,0,128)) #if alive set purple using the cell to rgb pixel map 
                elif cellDisplay[i][j] == 'GG':
                    strip.setPixelColor(rgbMap[i][j],Color(0,128,0)) #if alive set green using the cell to rgb pixel map 
                elif cellDisplay[i][j] == 'PG':
                    strip.setPixelColor(rgbMap[i][j],Color(0,0,128)) #if alive set blue using the cell to rgb pixel map 
                elif cellDisplay[i][j] == 'oo':
                    strip.setPixelColor(rgbMap[i][j],Color(128,80,0)) #if alive set orange using the cell to rgb pixel map 
                elif cellDisplay[i][j] == 'Po':
                    strip.setPixelColor(rgbMap[i][j],Color(128,0,128)) #if alive set purple using the cell to rgb pixel map 
                elif cellDisplay[i][j] == 'Go':
                    strip.setPixelColor(rgbMap[i][j],Color(0,128,0)) #if alive set green using the cell to rgb pixel map 
                else:
                    print('we have an error houston')
            else:
                strip.setPixelColor(rgbMap[i][j],Color(0,0,0))      #if dead turn off
    strip.show()

#map the RGB panel to the cellDisplay matrix
rgbCell = 0
for i in range(0,numOfRows-(2*unseenBorder), 2):
    for j in range(0,numOfColumns-(2*unseenBorder), 1):
        rgbMap[i][j] = rgbCell
        rgbCell = rgbCell + 1
    i = i + 1
    if i <= numOfRows-(2*unseenBorder): #dont go too far now!
        for k in range(numOfColumns-(2*unseenBorder)-1,0-1,-1): #we need to decriment start by extra 1, as its going backwards
            rgbMap[i][k] = rgbCell
            rgbCell = rgbCell + 1

if __name__ == '__main__':
        # Process arguments
        opt_parse()

        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        # Intialize the library (must be called once before other functions).
        strip.begin()

        while True:
            #colorWipeFast(strip, Color(0, 0, 0))  # Clear the Strip
            runSimulation()
            if isWorldStatic(): #if the world hasn't changed, lets add seeds
                generateSeeds()
            worldTrim()
            checkLifespan()

            current_milli_time = int(round(time.time() * 1000))  
            sleepTime = updateRate - (current_milli_time - last_milli_time)
            sleepTime = sleepTime * .001 #converting from millisconds to seconds for sleep function
            if (sleepTime < 0): #if we are behind schedule, don't sleep
                sleepTime = 0
            #print("Sleep time: ", sleepTime)
            time.sleep(sleepTime)
            last_milli_time = int(round(time.time() * 1000))

            displayWorld()
            cellCurrent = cellFuture