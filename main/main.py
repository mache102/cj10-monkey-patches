import logging

import pygame

from main.engine import Engine
from main.screens.game import GameScreen
from main.screens.main_menu import MainMenuScreen
from main.screens.levels import LevelsScreen
from main.screens.test import TestScreen

LOG_LEVEL = logging.DEBUG

logging.basicConfig()
logging.getLogger().setLevel(LOG_LEVEL)

pygame.init()


if __name__ == "__main__":
    engine = Engine()
    engine.add_screen("test", TestScreen())
    engine.add_screen("main_menu", MainMenuScreen())
    engine.add_screen("levels", LevelsScreen())
    engine.add_screen("game", GameScreen())

    engine.mainloop(init_screen="main_menu")
