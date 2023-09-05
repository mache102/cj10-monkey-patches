import logging

import pygame
from main.engine import Engine
from main.screens import TestScreen

logging.basicConfig()

pygame.init()


if __name__ == "__main__":
    engine = Engine()
    engine.add_screen("test", TestScreen())

    engine.mainloop(init_screen="test")
