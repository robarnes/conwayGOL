# conwayGOL
Conways Game of Life for RGB Matrices

There is likely little of novel value here, as [Conways Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) is well understood.  This repository is primarily a learning tool for me as I develop python and object oriented programming skills.

- **conway.py** was the first iteration.  Colors 'cells' based on age
- **geneticConway.py** was the second, and I added the concept of passive/recesive genes, with more information below
- **nextGenConway.py** is the current, using object oriented code.  This will eventually run on a 48x48 rgb panel.

There are two current game modes, which alternate on world resets.  Cells colors represent either their age or their genetic make up.

**Genetics:**
In conways game of life an empty/dead 'cell' with three neighbors becomes alive.  In my code each cell has a color gene, which defines what color it lights up on the rgb display.  When a new cell is to be born we randomly pick two of the three neighbors to be parents, and do a gene table lookup to see what color it should be.  Recessive genes are tracked.

Red = dominant  
Cyan = dominant  
Yellow = recessive  

Two of same dominant gene:
- Red|Red will display as Red
- Cyan|Cyan will display as Cyan

Dominant and recessive genes:
- Red|Yellow will display as Red
- Cyan|Yellow will display as Cyan

Two different dominant genes:
- Red|Cyan will display as Green

The rare-ish two recessive genes:
- Yellow|Yellow will display as Yellow

**Age:**
In the age-based game mode its a little easier to track the lifes of the cells as each round ticks by.  As the cells get older they change colors.

- Yellow : 0-4 cycles
- Red    : 5-14 cycles
- Green  : 15-59 cycles
- Cyan   : 60+ cycles
