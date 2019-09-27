#!/usr/bin/python
# class turorial : https://www.tutorialspoint.com/python/python_classes_objects.htm
# graphics tutorial : http://anh.cs.luc.edu/python/hands-on/3.1/handsonHtml/graphics.html


from graphics import *
import time
import random

numOfColumns = 50 #what can we see on your display
numOfRows = 50    #what can we see on your display

class Cell:
    'Common base class for all cells'
 
    def __init__(self,col,row):
        self.location = [col, row]
        self.genes = "xx"
        self.age = 0
        self.alive = 0
        self.aliveFuture = 0
 
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
    world = createWorld()  # create the world
    displayWorld(world) # display the world (used to clear the screen)

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

def displayWorld(world):
    #will do something here someday
    time.sleep(.1)

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
    for item in win.items[:]:
        item.undraw()
    win.update()
    for rowNumber in range(numOfRows):
        for colNumber in range(numOfColumns):
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
    time.sleep(.5)
            
win = GraphWin('planet', numOfRows*8, numOfColumns*8) # give title and dimensions
world = createWorld()
world = generateSeeds(world)
for x in range(100):
    world = runSimulation(world, numOfRows, numOfColumns)
    world = nextRound(world, numOfRows, numOfColumns)
    draw(world, numOfRows, numOfColumns, win)
    if checkDiversity(world, numOfRows, numOfColumns) == False:
        print("i can't live like this")
        world = generateSeeds(world)