import pygame
from constants import *
from game import Game
import ctypes

# dpi awareness
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Game")
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
    game = Game(win)
    game.run()
