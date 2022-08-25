import pygame

WIDTH, HEIGHT = 600, 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.field = False

    def draw(self):
        pass

def check_line(grid_cell, x, y):
    if x % 2 == 1 or y % 2 == 1:
        return False
    else:
        return True

grid_cell = [Cell(x, y) for x in range(5) for y in range(5)]    

while True:
    screen.fill(pygame.Color('black'))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            map_cell = [check_line(grid_cell, x, y) for y in range(5) for x in range(5)]
            for y in range(5):
                for x in range(5):
                    if map_cell[x + y * 5]:
                        print(" ", end="")
                    else:
                        print("#", end="")
                print()

    pygame.display.flip()
    clock.tick(30)