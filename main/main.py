import logging

import pygame

from main.engine import Engine
from main.screens.game import GameScreen
from main.screens.test import TestScreen

LOG_LEVEL = logging.DEBUG

logging.basicConfig()
logging.getLogger().setLevel(LOG_LEVEL)

pygame.init()


if __name__ == "__main__":
    engine = Engine()
    engine.add_screen("test", TestScreen())
    engine.add_screen("game", GameScreen())

    engine.mainloop(init_screen="game")
