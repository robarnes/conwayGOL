import time
import random
from neopixel import *
import argparse
import signal
import sys

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

numOfColumns = 48 #what can we see on your display
numOfRows = 48    #what can we see on your display

class Cell:
    'Common base class for all cells'
 
    def __init__(self,col,row):
        self.location = [col, row]
        self.genes = "PP"
        self.matrixLocation = 0

    def setLocation(self,location):
        self.matrixLocation = location

def createWorld():
    world = [[Cell(i, j) for i in range(numOfColumns)] for j in range(numOfRows)]  # create the world
    return world

def displayWorld(world, numOfRows, numOfColumns):
    for i in range(numOfRows):
        for j in range(numOfColumns):
            strip.setPixelColor(world[i][j].matrixLocation,Color(128,0,128))  #set to purple
            strip.show()
            time.sleep(1)
            strip.setPixelColor(world[i][j].matrixLocation,Color(0,0,0))      #turn off for next round

def rgbLedMapping(world):
    for rowNumber in range(0,16): #top 3 16x16 rgb panels
        for colNumber in range(0,48):
            location = (colNumber*16)+rowNumber
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber][colNumber].setLocation(location)

    for rowNumber in range(32,48): #bottom 3 16x16 rgb panels
        for colNumber in range(0,48):
            location = (colNumber*16)+(rowNumber-32)+1536
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber][colNumber].setLocation(location)

    for rowNumber in range(16,32): #middle row, left 16x16 panel
        for colNumber in range(0,16):
            location = (colNumber*16)+(rowNumber-16)+1280
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber][colNumber].setLocation(location)
            
    for rowNumber in range(16,32): #middle row, middle 16x16 panel
        for colNumber in range(16,32):
            location = (colNumber*16)+(rowNumber-16)+768
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber][colNumber].setLocation(location)

    for rowNumber in range(16,32): #middle row, right 16x16 panel
        for colNumber in range(32,48):
            location = (colNumber*16)+(rowNumber-16)+256
            #print("rowNumber: ", rowNumber, "colNumber: ", colNumber, "location: ", location)
            world[rowNumber][colNumber].setLocation(location)

    return world

#setup NeoPixels
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
args = parser.parse_args()
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

world = createWorld()
world = rgbLedMapping(world)

while True:
    #displayWorld(world, numOfRows, numOfColumns)
    print(world[0][0].matrixLocation)
    print(world[0][1].matrixLocation)
    print(world[0][2].matrixLocation)