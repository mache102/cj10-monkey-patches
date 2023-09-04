import logging

import pygame

from main.engine import Engine
from main.engine.text_rendering import LETTER_ASCII, render_to_surface

logging.basicConfig()

pygame.init()


if __name__ == "__main__":
    engine = Engine()

    test_text = render_to_surface(''.join(LETTER_ASCII), scale=3)
    text_sprite = pygame.sprite.DirtySprite()
    text_sprite.image = test_text
    text_sprite.rect = test_text.get_rect()
    engine.add_layer("test-widgets", pygame.sprite.RenderUpdates())
    engine.add_sprite("test-widgets", text_sprite)

    quick_fox_text = render_to_surface("The quick brown fox jumps over the lazy road-toad!".upper(), scale=3)
    fox_sprite = pygame.sprite.DirtySprite()
    fox_sprite.image = quick_fox_text
    fox_sprite.rect = quick_fox_text.get_rect()
    fox_sprite.rect.move_ip(0, text_sprite.rect.height + 18)
    engine.add_sprite("test-widgets", fox_sprite)

    engine.mainloop()
