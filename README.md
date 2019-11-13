# conwayGOL
Conways Game of Life for RGB Matrices

There is likely little of novel value here, as [Conways Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) is well understood.  This repository is primarily a learning tool for me as I develop python and object oriented programming skills.

- **conway.py** was the first iteration.  Colors 'cells' based on age
- **geneticConway.py** was the second, and I added the concept of passive/recesive genes, with more information below
- **nextGenConway.py** is the current, using object oriented code.  This will eventually run on a 48x48 rgb panel.

Potentially interesting aspects of this code:

**Genetics:**
In conways game of life an empty/dead 'cell' with three neighbors becomes alive.  In my code each cell has a color gene, which defines what color it lights up on the rgb display.  When a new cell is to be born we randomly pick two of the three neighbors to be parents, and do a gene table lookup to see what color it should be.  Recessive genes are tracked.

![Eye Color Genetics](https://github.com/robarnes/conwayGOL/blob/master/eye_color.jpg)

(P)urple = dominant  
(G)reen = dominant  
(o)range = recessive  

- PP will show Purple
- Po will show Purple
- GG will show Green
- Go will show Green
- PG will show Blue
- oo Will show Orange
