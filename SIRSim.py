import pygame, pygame.gfxdraw
import numpy as np
import random
import noise
from collections import defaultdict  # Needed for partition_cells function
import os

import csv

pygame.init()  # Initialize engine

clock = pygame.time.Clock()  # Set internal clock (prevents game from running on tick-speed)
pygame.font.init()
font = pygame.font.SysFont("timesnewroman", 36, bold=True, italic=False)

screen_info = pygame.display.Info()
screen_width, screen_height = int(screen_info.current_w), int(screen_info.current_h * 0.95)

# Cell size and grid setup
cell_size = 1
#grid_width, grid_height = screen_width // cell_size, screen_height // cell_size

# Initialize screen window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Infection Simulation")

# Pre-set colors
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
RED = (255, 0, 0)
SOFTRED = (255, 0, 0, 20)
BLUE = (255, 255, 255)
GREEN = GRAY#(0, 255, 0)
BLACK = (0,0,0)

# Define Cell class
class Cell:
    def __init__(self, x, y, susceptible=True, infectious=False, dead=False, recovered=False, color=BLUE, infect_time=None, sideweight = 0, immortal = False):
        self.x = x
        self.y = y
        self.susceptible = susceptible
        self.infectious = infectious
        self.dead = dead
        self.recovered = recovered
        self.color = color
        self.infect_time = infect_time
        self.speed = random.randint(25, 35)  # Random move-speed
        self.ttr = random.randint(5, 15)  # Time to recover/die
        self.time_x = random.uniform(0, 1000)
        self.time_y = random.uniform(0, 1000)
        self.time_x2 = random.uniform(0, 1000)
        self.time_y2 = random.uniform(0, 1000)
        self.bias = random.randint(17, 32)
        self.hyperweight = 1
        self.denseweight = 0
        self.sideweight = sideweight
        self.immortal = immortal
        hyper = random.randint(0, 5)
        if hyper == 1:
            self.hyperweight = random.randint(10,  20)/10

    def move(self, dt):
        if self.dead:
            return  # Dead cells do not move
        # if self.infectious and self.x <= screen_width/2:
        #     self.denseweight = .5
        # if self.infectious and self.x >= screen_width/2:
        #     self.denseweight = 0
        self.time_x += dt
        self.time_y += dt
        noise_x = noise.pnoise1(self.time_x) * self.bias
        noise_y = noise.pnoise1(self.time_y) * self.bias
        mod_x = noise.pnoise1(self.time_x2) + 1.5
        mod_y = noise.pnoise1(self.time_y2) + 1.5
        self.x += noise_x * dt * 2 * self.hyperweight * mod_x + self.sideweight
        self.y += noise_y * dt * 2 * self.hyperweight * mod_y

    def kill_recover(self):
        prob = random.randint(0, 100)
        if prob <= 20:
            self.susceptible = False
            self.infectious = False
            self.dead = True
            self.recovered = False
            self.color = GRAY
        else:
            self.susceptible = False
            self.infectious = False
            self.dead = False
            self.recovered = True
            self.color = GREEN

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.color,
            (self.x * cell_size, self.y * cell_size, cell_size, cell_size)
        )


def draw_glow(screen, x, y, radius, color):
    pygame.gfxdraw.filled_circle(screen, x, y, radius, color)
    pygame.gfxdraw.aacircle(screen, x, y, radius, color)


def partition_cells(cells, cell_size):
    grid_partition = defaultdict(list)
    for cell in cells:
        grid_x = int(cell.x // cell_size)
        grid_y = int(cell.y // cell_size)
        grid_partition[(grid_x, grid_y)].append(cell)
    return grid_partition


def infect(cells, partition, cell_size, base_distance=1):
    grid_size = cell_size * 2
    scaled_distance = base_distance

    for cell in cells:
        if not cell.susceptible:
            continue

        grid_x = int(cell.x // grid_size)
        grid_y = int(cell.y // grid_size)
        neighbors = []

        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                neighbors.extend(partition.get((grid_x + dx, grid_y + dy), []))

        for neighbor in neighbors: # iterate through nearby cells
            if neighbor.infectious: # check if any nearby cells are infection
                distance = ((cell.x - neighbor.x) ** 2 + (cell.y - neighbor.y) ** 2) ** 0.5 # Pythagorean distance formula
                if distance <= 50: # check if distance to nearby cell is within infection range (6 in this case)
                    cell.susceptible = False # Revert out of susceptible state
                    cell.infectious = True # Set infectious state
                    cell.infect_time = pygame.time.get_ticks() # Handles later logic, ignore for now
                    cell.color = RED # set cell color
                    break


def populate_zone(cell_count, init_infected, x=(0, screen_width), y=(0, screen_height), sideweight=0, immortal=False):
    x_min, x_max = x
    y_min, y_max = y
    cells = []
    for _ in range(cell_count - init_infected):
        x = random.uniform(x_min, x_max - cell_size) / cell_size
        y = random.uniform(y_min, y_max - cell_size) / cell_size
        cells.append(Cell(x, y, susceptible=True, infectious=False, dead=False))
    for _ in range(init_infected):
        x = random.uniform(x_min, x_max - cell_size) / cell_size
        y = random.uniform(y_min, y_max - cell_size) / cell_size
        cells.append(Cell(x, y, susceptible=False, infectious=True, dead=False, color=RED, infect_time=pygame.time.get_ticks()))
    return cells

def composite_zones(*zones):
    population = []
    for zone in zones:
        for cell in zone:
            population.append(cell)
    return population



zone_main = populate_zone(10000, 3, [0, screen_width])
cells = composite_zones(zone_main)
running = True
simulation_over = False  # Flag to detect if the simulation is over

base_filename = "./sims/simlog"
counter = 1

if not os.path.exists("./sims"):
    os.makedirs("./sims")

while os.path.exists(f"{base_filename}_{counter}.csv"):
    counter += 1

filename = f"{base_filename}_{counter}.csv"

with open(filename, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Time (s)", "Susceptible", "Infectious", "Recovered", "Dead"])

    last_log_time = 0

    while running:
        dt = clock.tick(60) / 1000
        current_time = pygame.time.get_ticks() / 1000  # Current time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if simulation_over:
            # Display end message
            end_text = font.render("Simulation Complete", True, WHITE)
            end_rect = end_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(end_text, end_rect)
            pygame.display.flip()
            continue  # Skip further updates if simulation is over

        screen.fill(BLACK)

        # Count the population states
        num_susceptible = sum(1 for cell in cells if cell.susceptible)
        num_infectious = sum(1 for cell in cells if cell.infectious)
        num_recovered = sum(1 for cell in cells if cell.recovered)
        num_dead = sum(1 for cell in cells if cell.dead)

        # Display stats on screen
        stats_text = font.render(
            f"Susceptible: {num_susceptible} Infectious: {num_infectious} Recovered: {num_recovered} Dead: {num_dead}",
            True, (0, 0, 0))
        screen.blit(stats_text, (10, 10))

        #Log data to CSV every 0.5 seconds
        if current_time - last_log_time >= 0.5:
            csv_writer.writerow([round(current_time, 2), num_susceptible, num_infectious, num_recovered, num_dead])
            last_log_time = current_time

        #Check if simulation is over
        if num_infectious == 0:
            simulation_over = True
            continue

        # Update infection logic
        partition = partition_cells(cells, cell_size * 2)
        infect(cells, partition, cell_size)

        # Update cell states
        for cell in cells:
            if cell.infect_time is not None:
                elapsed_time = (pygame.time.get_ticks() - cell.infect_time) / 1000
                if elapsed_time >= cell.ttr and not cell.dead and not cell.recovered and not cell.immortal:
                    cell.kill_recover()

        # Move and draw cells
        for cell in cells:
            cell.move(dt)
            if cell.infectious:
                draw_glow(screen, int(cell.x * cell_size), int(cell.y * cell_size), radius=5*cell_size, color=SOFTRED)
            cell.draw(screen)

        pygame.display.flip()
