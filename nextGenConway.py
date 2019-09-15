#!/usr/bin/python
# class turorial : https://www.tutorialspoint.com/python/python_classes_objects.htm
# graphics tutorial : http://anh.cs.luc.edu/python/hands-on/3.1/handsonHtml/graphics.html


from graphics import *

numOfColumns = 4 #what can we see on your display
numOfRows = 4    #what can we see on your display

class Cell:
    'Common base class for all cells'
 
    def __init__(self,col,row):
        self.location = [col, row]
        self.genes = "xx"
        self.age = 0
        self.alive = 0
        self.aliveFuture = 0
    
    def displayCellInfo(self):
        print("Location : ", self.location[0], ",", self.location[1],  ", Genes: ", self.genes)
        print("Alive: ",self.alive, " Future Alive: ",self.aliveFuture)
 
    def kill(self):
        self.aliveFuture = 0
    
    def resurrect(self):
        self.aliveFuture = 1

    def futureGenes(self,genes):
        self.genes = genes

world = [[Cell(i,j) for i in range(numOfColumns)] for j in range(numOfRows)] #create the world
#world[0][0] = Cell(0,0, "GG")

world[0][0].displayCellInfo()
world[0][0].resurrect()
world[0][0].displayCellInfo()
world[0][0].kill()
world[0][0].futureGenes("yy")
world[0][0].displayCellInfo()










def draw():
    win = GraphWin('world', 200, 150) # give title and dimensions
    #win.yUp() # make right side up coordinates!

    dot1 = Circle(Point(2,2), 1) # set center and radius
    dot1.setFill("yellow")
    dot1.draw(win)

    message = Text(Point(win.getWidth()/2, 20), 'Click anywhere to quit.')
    message.draw(win)
    win.getMouse()
    win.close()