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

#minimum of 21
numOfColumns = 36 #we chop 10 off each side when we display so it looks better
numOfRows = 36    #otherwise you get a bunch of alive cells along the edge

cellCurrent = [[0 for i in range(numOfColumns)] for j in range(numOfRows)]  #create an empty matrix
cellFuture = [[0 for i in range(numOfColumns)] for j in range(numOfRows)]  #create an empty matrix
cellDisplay = [[0 for i in range(numOfColumns-20)] for j in range(numOfRows-20)]  #create an empty matrix
cellLifespan = [[0 for i in range(numOfColumns-20)] for j in range(numOfRows-20)]  #create an empty matrix
rgbMap = [[0 for i in range(numOfColumns-20)] for j in range(numOfRows-20)]  #create an empty matrix

staticWorldCount = 0 #this is used to see if world has become static / non-changing
staticWorldLastCellCount = 0 #used to count how many cycles the qty. of cells is static

def generateSeeds():
    numberOfSeeds = int((numOfColumns*numOfRows)*.1) #lets seed the world with about 10%
    for x in range(numberOfSeeds):
        #cellCurrent[random.randint(0,numOfRows-1)][random.randint(0,numOfColumns-1)] = 1 #lets add some life seeds
	seedRow = random.randint(0,numOfRows-1)
	seedCol = random.randint(0,numOfColumns-1)
	cellCurrent[seedRow][seedCol] = 1
	if 10 < seedRow < numOfRows-11:
		if 10 < seedCol < numOfColumns-11: #only show if in display area
		        strip.setPixelColor(rgbMap[seedRow-10][seedCol-10],Color(255,128,64))      #lets show where new seeds landed!
    strip.show()
    time.sleep(2) #dramatic pause

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
                numNeighbors = numNeighbors + (cellCurrent[rowNumber+rowShift][colNumber+colShift])
    if cellCurrent[rowNumber][colNumber] == 1:  #lets not count ourselves, ok?
        numNeighbors = numNeighbors - 1
    return numNeighbors

def checkLife(cellCurrent, rowNumber, colNumber):
    if neighbors(cellCurrent, rowNumber, colNumber) == 3: #does this cell have three neighbors?
        cellFuture[rowNumber][colNumber] = 1
    if cellCurrent[rowNumber][colNumber] == 1:  #only check if already alive
        if neighbors(cellCurrent, rowNumber, colNumber) < 2: #do you have less than two neighbors?
            cellFuture[rowNumber][colNumber] = 0
        elif neighbors(cellCurrent, rowNumber, colNumber) > 3: #do you have more than 3 neighbors?
            cellFuture[rowNumber][colNumber] = 0

def runSimulation():
    for i in range(numOfRows):
        for j in range(numOfColumns):
            checkLife(cellCurrent, j, i)

def worldTrim():
    for i in range(10,numOfRows-10, 1): #here we chop 10 rows/columns off each side of the world to make it look better
        for j in range(9,numOfColumns-10, 1):
            cellDisplay[i-10][j-10] = cellFuture[i][j]

def isWorldStatic():
    global staticWorldLastCellCount
    global staticWorldCount
    staticWorldCurrentCellCount = np.sum(cellDisplay)
    if staticWorldLastCellCount == staticWorldCurrentCellCount: #we have same number of cells as last time?
        staticWorldCount = staticWorldCount + 1
        print(staticWorldCount) #just debugging
    else:
        staticWorldCount = 0
    staticWorldLastCellCount = staticWorldCurrentCellCount
    if staticWorldCurrentCellCount == 0: #everyone is dead, add seeds
        return True
    elif staticWorldCount >= 60: #boooring.  add seeds
        return True
    else:
        return False #everything is cool

def checkLifespan():
    for i in range(numOfRows-20):
        for j in range(numOfColumns-20):
            if cellDisplay[i][j] == 1: #lets see if we are alive
                cellLifespan[i][j] = cellLifespan[i][j] + 1 #add to age
            else: #set age to zero
                cellLifespan[i][j] = 0

def displayWorld():
    #print(np.matrix(cellDisplay)) #show the world
    #print(np.matrix(rgbMap)) #show the world
    #print(np.matrix(cellLifespan)) #show how long each cell is alive
    #print(np.sum(cellDisplay))  #show total number of cells alive
    for i in range(0,numOfRows-20, 1):
        for j in range(0,numOfColumns-20, 1):
            if cellDisplay[i][j] == 1:
		if cellLifespan[i][j] > 60:
                	strip.setPixelColor(rgbMap[i][j],Color(0,0,128)) #if alive set blue using the cell to rgb pixel map
		elif cellLifespan[i][j] > 15:
                	strip.setPixelColor(rgbMap[i][j],Color(0,0,160)) #if alive set blue using the cell to rgb pixel map
		elif cellLifespan[i][j] > 5:
                	strip.setPixelColor(rgbMap[i][j],Color(128,128,0)) #if alive set blue using the cell to rgb pixel map
		else:
                	strip.setPixelColor(rgbMap[i][j],Color(0,64,90)) #if alive set blue using the cell to rgb pixel map
            else:
                strip.setPixelColor(rgbMap[i][j],Color(0,0,0))      #if dead turn off
    strip.show()

#map the RGB panel to the cellDisplay matrix
rgbCell = 0
for i in range(0,numOfRows-20, 2):
    for j in range(0,numOfColumns-20, 1):
        rgbMap[i][j] = rgbCell
        rgbCell = rgbCell + 1
    i = i + 1
    if i <= numOfRows-20: #dont go too far now!
        for k in range(numOfColumns-20-1,0-1,-1): #we need to decriment start by extra 1, as its going backwards
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
            if isWorldStatic(): #if the world hasn't changed, lets add seeds
                generateSeeds()
            runSimulation()
            worldTrim()
            checkLifespan()
            displayWorld()
            cellCurrent = cellFuture
            time.sleep(1)

#print(np.shape(cellCurrent))
