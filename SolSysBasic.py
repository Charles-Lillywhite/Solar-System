# import modules
import pygame
import math
from random import randint, uniform
from astropy.time import Time
from astroquery.jplhorizons import Horizons
import datetime
pygame.font.init()
pygame.init()

# define window params
WINDOW_HEIGHT = 800
H_OFFSET = 385
WINDOW_WIDTH = 800 
W_OFFSET = 435
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Solar System Simulation')

# define colours to use
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 140, 240)
RED = (185, 40, 50)
DARK_GREY = (80, 75, 80)
# define font for displaying date
FONT = pygame.font.SysFont('Times', 25)

# define planet class, attributes, methods.
class Planet:
    
    AU = 1.495979e11 # metres in 1 Astronomical Unit
    G = 6.67428e-11 # Newton's Gravitational Constant
    TIME_DELTA = 60*60*24 # number of seconds in an Earth day
    INV_TD = 1/TIME_DELTA # for converting units of Horizons position/velocity 
    SCALE = 245 / AU # scale of pixels per AU, all orbits should fit in WINDOW
    
    DATE = datetime.date(2022, 1, 1) # start date of simulation
        
    def __init__(self, x, y, radius, mass, colour):
        
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.colour = colour
        
        self.x_velocity = 0
        self.y_velocity = 0
        
        self.orbit = []
        self.draw_orbit = []
        
    def draw(self, WINDOW):
        # convert physical distances to pixel locations 
        a = self.x * Planet.SCALE + (W_OFFSET) 
        b = self.y * Planet.SCALE + (H_OFFSET)
        self.draw_orbit.append((a, b))
        
        # draw orbital path
        #if len(self.orbit) > 2:
            #pygame.draw.lines(WINDOW, WHITE, False, self.draw_orbit, width = 2)
            
        # draw planet
        pygame.draw.circle(WINDOW, self.colour, (a, b), self.radius)
        
    def gravitation(self, other):
        
        other_x = other.x
        other_y = other.y
        delta_x = other_x - self.x
        delta_y = other_y - self.y
        separation = math.sqrt(delta_x ** 2 + delta_y ** 2)
        
        force = (Planet.G * self.mass * other.mass) / (separation ** 2)
        theta = math.atan2(delta_y, delta_x)
        force_x = force * math.cos(theta)
        force_y = force * math.sin(theta)
        
        return (force_x, force_y)
        
    def evolve(self, planets):
    
        tot_force_x = 0
        tot_force_y = 0
        
        for planet in planets:
            
            if planet == self:
                continue
            
            f_x, f_y = self.gravitation(planet)
            tot_force_x += f_x
            tot_force_y += f_y
            
        accel_x = tot_force_x / self.mass
        accel_y = tot_force_y / self.mass
        
        self.x_velocity += accel_x * Planet.TIME_DELTA
        self.y_velocity += accel_y * Planet.TIME_DELTA
        
        self.x += self.x_velocity * Planet.TIME_DELTA
        self.y += self.y_velocity * Planet.TIME_DELTA
        
        self.orbit.append((self.x, self.y))
        
    def display_date():
        curr_date = FONT.render(f'{Planet.DATE}', False, WHITE)
        WINDOW.blit(curr_date, (10, 10))
        
        Planet.DATE += datetime.timedelta(days = 1)

# make an aesthetic background
class BGstar:
    zoom = Planet.SCALE
    
    
    def __init__(self):
        self.x = randint(-2*Planet.AU, 2*Planet.AU)
        self.y = randint(-2*Planet.AU, 2*Planet.AU)
        
        self.radius = uniform(1.0, 2.5)
        self.colour = WHITE
        
    def drawStar(self):
        a = self.x * BGstar.zoom + (W_OFFSET) 
        b = self.y * BGstar.zoom + (H_OFFSET)
        pygame.draw.circle(WINDOW, self.colour, (a, b), self.radius)

    
stars = [BGstar() for i in range(200)]

        
def simulate():
    
    running = True
    paused = False
    
    
    clock = pygame.time.Clock()
    
    sun = Planet(0, 0, 28, 1.98892e30, YELLOW)

    earth_ICs = Horizons(id = 3, location="@sun", epochs=Time(str(Planet.DATE)).jd, id_type='id').vectors()
    earth = Planet(earth_ICs['x'][0] * Planet.AU , earth_ICs['y'][0] * Planet.AU , 16, 5.9742e24, BLUE)
    earth.x_velocity = -earth_ICs['vx'][0] * Planet.AU * Planet.INV_TD
    earth.y_velocity = -earth_ICs['vy'][0] * Planet.AU * Planet.INV_TD

    
    mars_ICs = Horizons(id = 4, location="@sun", epochs=Time(str(Planet.DATE)).jd, id_type='id').vectors()
    mars = Planet(mars_ICs['x'][0] * Planet.AU , mars_ICs['y'][0] * Planet.AU , 12, 6.39e23, RED)
    mars.x_velocity = -mars_ICs['vx'][0] * Planet.AU * Planet.INV_TD
    mars.y_velocity = -mars_ICs['vy'][0] * Planet.AU * Planet.INV_TD

    mercury_ICs = Horizons(id = 1, location="@sun", epochs=Time(str(Planet.DATE)).jd, id_type='id').vectors()
    mercury = Planet(mercury_ICs['x'][0] * Planet.AU , mercury_ICs['y'][0] * Planet.AU, 8, 3.30e23, WHITE)
    mercury.x_velocity = -mercury_ICs['vx'][0] * Planet.AU * Planet.INV_TD
    mercury.y_velocity = -mercury_ICs['vy'][0] * Planet.AU * Planet.INV_TD

    venus_ICs = Horizons(id = 2, location="@sun", epochs=Time(str(Planet.DATE)).jd, id_type='id').vectors()
    venus = Planet(venus_ICs['x'][0] * Planet.AU , venus_ICs['y'][0] * Planet.AU, 14, 4.8685e24, DARK_GREY)
    venus.x_velocity = -venus_ICs['vx'][0] * Planet.AU * Planet.INV_TD
    venus.y_velocity = -venus_ICs['vy'][0] * Planet.AU * Planet.INV_TD

    planets = [sun, earth, mars, mercury, venus]
    
    while running:
        

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE:# Pausing/Unpausing
                    paused = not paused
                    
                if event.key == pygame.K_i:
                    Planet.SCALE *= 1.1
                    BGstar.zoom *= 1.005
                    for planet in planets:
                        planet.radius *= 1.1
                    
                if event.key == pygame.K_o:
                    Planet.SCALE *= 0.90909
                    BGstar.zoom *= 0.99502
                    for planet in planets:
                        planet.radius *= 0.90909

        
        if not paused:
            
            clock.tick(45)
            WINDOW.fill((0, 0, 0))
            Planet.display_date()
            for star in stars:
                BGstar.drawStar(star)
            for planet in planets:
                planet.evolve(planets)
                planet.draw(WINDOW)
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == '__main__':
    simulate()
