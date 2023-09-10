import logging
from pathlib import Path

import pygame
from PIL import Image

from main.engine import Engine, Screen, components, text_rendering
from main.engine.text_rendering import LETTER_ASCII
from main.image_ops import (
    conv_img_arr_to_tile, conv_pil_to_numpy, flip_tiles, rotate_tiles
)


class TestButton(components.BaseComponent):
    """A count button."""

    count: int = 0

    def __init__(self):
        super().__init__()
        # width, height
        self.set_size((200, 50))

        # x, y
        self.set_position((100, 100))

        self.render_text()

    def render_text(self):
        """Render the text."""
        # Erase our image
        button_image_path = Image.open(Path(__file__).parent.parent / 'data' / 'Images' / 'button.png')
        button_image = conv_pil_to_numpy(button_image_path)
        self.set_9_slice_surface(button_image, border=(4, 4, 4, 4), scale=4)

        offset = text_rendering.width_of_rendered_text(str(self.count), scale=4) + 4

        self.set_text(
            str(self.count),
            position=(self.size[0] - offset, 10),
            color=(0, 0, 0),
            scale=4,
        )

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.count += 1
        print(self.count)
        self.render_text()

    def on_mouse_enter(self, event: pygame.event.Event):
        """Called when the mouse enters the component."""
        print("Mouse entered button")

    def on_mouse_leave(self, event: pygame.event.Event):
        """Called when the mouse leaves the component."""
        print("Mouse left button")


class TestScreen(Screen):
    """A test screen."""

    logger: logging.Logger

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing test screen")

        engine.background_color = (0, 255, 0)
        engine.add_layer("test-widgets")

        test_text = components.Text(''.join(LETTER_ASCII))
        engine.add_sprite("test-widgets", test_text)

        quick_fox_text = components.Text("The quick brown fox jumps over the lazy road-toad!")
        quick_fox_text.set_position((
            quick_fox_text.position[0],
            quick_fox_text.position[1] + quick_fox_text.rect.height + 18,
        ))
        engine.add_sprite("test-widgets", quick_fox_text)

        engine.add_sprite("test-widgets", TestButton())

        logo_png = Image.open(Path(__file__).parent.parent / 'data/Images/pydis_logo.png')
        img_arr = conv_pil_to_numpy(logo_png)
        logo = components.Image(img_arr, (454, test_text.rect.height + 54))
        engine.add_sprite("test-widgets", logo)

        # Test img ops
        # Remember to delete the arrays after
        surface_arr = pygame.surfarray.pixels3d(logo.image)
        tile_arr = conv_img_arr_to_tile(surface_arr, 100)
        rotate_tiles(tile_arr, (0, 0), (0, 1), rotation=90)
        flip_tiles(tile_arr, (1, 0), axis='horizontal')
        del surface_arr, tile_arr

        self.logger.info("Initialized test screen")
