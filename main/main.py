import logging
from pathlib import Path

import pygame
from PIL import Image

from main.engine import Engine
from main.engine.text_rendering import LETTER_ASCII, render_to_surface
from main.engine.utils import make_surface_rgba
from main.image_ops import (
    conv_img_arr_to_tile, conv_pil_to_numpy, flip_tiles, rotate_tiles
)

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

    logo_png = Image.open(Path(__file__).parent / 'data/Images/pydis_logo.png')
    img_arr = conv_pil_to_numpy(logo_png)
    test_img = make_surface_rgba(img_arr, scale=1)
    img_sprite = pygame.sprite.DirtySprite()
    img_sprite.image = test_img
    img_sprite.rect = test_img.get_rect()
    img_sprite.rect.move_ip(454, text_sprite.rect.height + 54)
    engine.add_sprite("test-widgets", img_sprite)

    # Test img ops
    # Remember to delete the arrays after
    surface_arr = pygame.surfarray.pixels3d(img_sprite.image)
    tile_arr = conv_img_arr_to_tile(surface_arr, 100)
    rotate_tiles(tile_arr, (0, 0), (0, 1), rotation=90)
    flip_tiles(tile_arr, (1, 0), axis='horizontal')
    del surface_arr, tile_arr

    engine.mainloop()
