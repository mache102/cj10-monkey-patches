import logging

import pygame

from main.engine import Engine
from main.screens.credits import CreditsScreen
from main.screens.game import GameScreen
from main.screens.levels import LevelsScreen
from main.screens.main_menu import MainMenuScreen
from main.screens.test import TestScreen

LOG_LEVEL = logging.DEBUG

logging.basicConfig()
logging.getLogger().setLevel(LOG_LEVEL)

pygame.init()

# Note: When you add an image, append the tile size to the end of this tuple
# and call the image "puzzle{}.png"
puzzle_tile_sizes = (100, 200, 64, 128, 60)

if __name__ == "__main__":
    engine = Engine()
    engine.add_screen("test", TestScreen())
    engine.add_screen("main_menu", MainMenuScreen())
    engine.add_screen("levels", LevelsScreen(len(puzzle_tile_sizes)))
    for puzzle_no, tile_size in enumerate(puzzle_tile_sizes):
        engine.add_screen(f"game{puzzle_no}", GameScreen(puzzle_no, tile_size))
    engine.add_screen("credits", CreditsScreen())

    engine.mainloop(init_screen="main_menu")
