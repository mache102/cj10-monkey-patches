import logging
import pygame
from main.engine import Engine

logging.basicConfig()

pygame.init()


if __name__ == "__main__":
    engine = Engine()

    engine.mainloop()
