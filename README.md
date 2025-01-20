# SIRSim
Proximal disease simulation developed as a freshman for rudimentary computer science course. Based off of SIR (Susceptible-Infected-Recovered) epidemiological model. 

Please note that this first version is very rough around the edges, with improvements to be made in the future.

## Modules

This simulation requires several modules to run from an IDE. Use
```pip install pygame pygame.gfxdraw numpy random noise```

Pygame runs the sim in a window, with the gfxdraw module handling several draw calls within the engine. Numpy is not currently implemented but will be in future versions for networked movement. random is used for several random cell properties, and noise is used for pseudo random vectorized movement.
The world sizw is directly proportional to your screen size. 

## Populating the world

To populate the world, there are 2 steps.

### Step 1 
... is to use the `populate_zone()` function to encode a single cell zone. this funtion takes 4 arguments;
- `cell_count`, which is how many cells you want the zone to have.
- `init_infected` dictates how many cells out of that cell count you want to start infected.
- `x` and `y` define the zone's bounding box. By default the zone occupies the entire area of the screen (`x=(0, screen_width)`, `y=(0, screen_height)`) but it can be modified by setting them equal to a 2 value tuple with a low bound and upper bound. An unlimited amount of zones can be created. To make things scale nicely, and for general ease, the screen dimension variables are just integers so they can be divided to make populating zones with relative dimensions easier. For example, to generate 2 zones that each occupy one half of the screen, the x bounds for the left zone would be `(0, screen_width/2)`, while the right zone would have bounds `(screen_width/2, screen_width)`
- `sideweight` is a mechanic I integrated for fun. It dictates x-direction move influence for cells that spawn infected. This could be fun to play around with, but for general purpose I usually keep it off. negative values influence movement to the left, whereas positive values influence movement to the right (defaulted to 0).
- `immortal` is another for-fun mechanic. It removes the death/recovery timer from initially spawned infected cells so that they stay infected for the entire duration of the simulation.

### Step 2

... is to to use the `composite_zones` function to compile all zones together. To use this, just pass through the name of every zone variable you created.
PLEASE NOTE THAT YOU __MUST__ USE THIS FUNCTION EVEN IF YOU ONLY MADE ONE ZONE
