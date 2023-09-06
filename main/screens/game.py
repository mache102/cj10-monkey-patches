import logging
from pathlib import Path

import numpy as np
import pygame
from PIL import Image
from pydantic import BaseModel

from main import image_ops
from main.engine import Engine, Screen, components, utils
from main.image_ops import conv_img_arr_to_tile, conv_pil_to_numpy
from main.type_aliases import ImageArray, TileArray


class ScrambleConfig(BaseModel):
    """Configuration for scrambling image"""

    tile_size: int
    path: Path  # Relative to data/Images
    outline_thickness: int
    outline_color: tuple[int, int, int, int]


class ScrambledImage(components.BaseComponent):
    """Scrambled image, with the ability to select tiles."""

    config: ScrambleConfig
    tile_arr: TileArray
    selected_tile: tuple[int, int]
    fit_size: tuple[int, int]

    image_array: ImageArray
    select_array: ImageArray

    def __init__(self, scramble_config: ScrambleConfig):
        super().__init__()

        self.config = scramble_config

        # Open iamge array
        logo_png = Image.open(Path(__file__).parent.parent / 'data' / 'Images' / scramble_config.path)
        self.image_array = utils.add_alpha_to_arr(conv_pil_to_numpy(logo_png))
        self.fit_size = self.image_array.shape[:2]

        self.tile_arr = conv_img_arr_to_tile(self.image_array, self.config.tile_size)
        self.selected_tile = (0, 0)

        self.update_surface()

        self.logger = logging.getLogger(__name__)

    def on_click(self, event: pygame.event.Event):
        """Called when the image is clicked."""
        local_pos = event.pos[0] - self.position[0], event.pos[1] - self.position[1]

        self.logger.debug(f"Clicked tile at local pos {local_pos}")
        self.selected_tile = self.get_tile_index(local_pos)
        self.logger.debug(f"Selected tile is {self.selected_tile}")
        self.update_surface()

    def on_key_press(self, event: pygame.event.Event):
        """Tile selection with arrow keys."""
        new_selected_tile = self.selected_tile

        if event.key == pygame.K_LEFT:
            self.logger.debug("Pressed LEFT key")
            new_selected_tile = (self.selected_tile[0] - 1, self.selected_tile[1])
        elif event.key == pygame.K_RIGHT:
            self.logger.debug("Pressed RIGHT key")
            new_selected_tile = (self.selected_tile[0] + 1, self.selected_tile[1])
        elif event.key == pygame.K_UP:
            self.logger.debug("Pressed UP key")
            new_selected_tile = (self.selected_tile[0], self.selected_tile[1] - 1)
        elif event.key == pygame.K_DOWN:
            self.logger.debug("Pressed DOWN key")
            new_selected_tile = (self.selected_tile[0], self.selected_tile[1] + 1)

        # image operations
        # q key
        # elif event.key == pygame.K_q:
        #     self.logger.debug(f"Pressed Q key")
        #     image_ops.flip_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
        #     self.scrambled_image.update_surface()

        # elif event.key == pygame.K_w:
        #     self.logger.debug(f"Pressed W key")
        #     image_ops.rotate_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
        #     self.scrambled_image.update_surface()

        if not np.allclose(new_selected_tile, self.selected_tile):
            # Check if the new selected tile is within bounds
            rows, cols = self.image_array.shape[:2]
            new_selected_tile = (
                np.clip(new_selected_tile[0], 0, (rows // self.config.tile_size) - 1),
                np.clip(new_selected_tile[1], 0, (cols // self.config.tile_size) - 1)
            )

            self.logger.debug(f"New selected tile: {new_selected_tile}")

            self.selected_tile = new_selected_tile
            self.update_surface()

    def get_tile_index(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Get the index of the tile at the given local position."""
        return (
            int(pos[0] / self.fit_size[0] * self.image_array.shape[0]) // self.config.tile_size,
            int(pos[1] / self.fit_size[1] * self.image_array.shape[1]) // self.config.tile_size,
        )

    def update_surface(self):
        """Rerender the surface."""
        self.select_array = np.zeros(self.image_array.shape, dtype=np.uint8)
        position = self.selected_tile[0] * self.config.tile_size, self.selected_tile[1] * self.config.tile_size
        size = self.config.tile_size, self.config.tile_size

        # Create the outline rectangle
        rect = utils.outline_rectangle(size, self.config.outline_color, self.config.outline_thickness)
        self.select_array[position[0]:position[0] + size[0], position[1]:position[1] + size[1]] = rect

        actual_image = utils.merge_images(self.select_array, self.image_array)
        actual_image = utils.stretch_arr(actual_image, self.fit_size)
        self.set_size(self.fit_size)
        self.set_surface(actual_image)


class ImageOpButton(components.LabeledButton):
    """Image operation button"""

    scrambled_image: ScrambledImage

    def __init__(self, op_name: str, size: tuple[int, int], scrambled_image: ScrambledImage):
        super().__init__(op_name, size=size)
        self.scrambled_image = scrambled_image


class FlipButton(ImageOpButton):
    """A flip button."""

    def __init__(self, scrambled_image: ScrambledImage):
        super().__init__("FLIP", size=(200, 50), scrambled_image=scrambled_image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        image_ops.flip_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
        self.scrambled_image.update_surface()

    def on_key_press(self, event: pygame.event.Event):
        """Called when the keyboard shortcut is pressed."""
        if event.key == pygame.K_q:
            image_ops.flip_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
            self.scrambled_image.update_surface()


class RotateButton(ImageOpButton):
    """A rotate button."""

    def __init__(self, scrambled_image: ScrambledImage):
        super().__init__("ROTATE", size=(200, 50), scrambled_image=scrambled_image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        image_ops.rotate_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
        self.scrambled_image.update_surface()

    def on_key_press(self, event: pygame.event.Event):
        """Called when the keyboard shortcut is pressed."""
        if event.key == pygame.K_w:
            image_ops.rotate_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
            self.scrambled_image.update_surface()


class SwapButton(ImageOpButton):
    """A swap button."""

    def __init__(self, scrambled_image: ScrambledImage):
        super().__init__("SWAP", size=(200, 50), scrambled_image=scrambled_image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Swapped")


class FilterButton(ImageOpButton):
    """A filter button."""

    def __init__(self, scrambled_image: ScrambledImage):
        super().__init__("FILTER", size=(200, 50), scrambled_image=scrambled_image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Filtered")


class GameScreen(Screen):
    """The game screen."""

    logger: logging.Logger

    image: ScrambledImage
    flip_button: FlipButton
    rotate_button: RotateButton
    swap_button: SwapButton
    filter_button: FilterButton

    SCALE: int = 4

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game screen")

        engine.background_color = (240, 240, 240)

        # Image
        engine.add_layer("image", pygame.sprite.RenderUpdates())

        scramble_config = ScrambleConfig(  # TODO: Use level configs
            tile_size=100,
            path=Path("pydis_logo.png"),
            outline_thickness=4,
            outline_color=(0, 0, 0, 255),
        )
        self.image = ScrambledImage(scramble_config)

        engine.add_sprite("image", self.image)

        # Buttons
        engine.add_layer("buttons", pygame.sprite.RenderUpdates())

        self.flip_button = FlipButton(self.image)
        self.rotate_button = RotateButton(self.image)
        self.swap_button = SwapButton(self.image)
        self.filter_button = FilterButton(self.image)

        engine.add_sprite("buttons", self.flip_button)
        engine.add_sprite("buttons", self.rotate_button)
        engine.add_sprite("buttons", self.swap_button)
        engine.add_sprite("buttons", self.filter_button)

        self.size_components(engine.display.get_size())

        self.logger.info("Initialized game screen")

    def on_event(self, engine: Engine, delta_time: float, events: list[pygame.event.Event]):
        """Called when an event occurs."""
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.size_components((event.w, event.h))

    def on_end(self, engine: Engine):
        """Called when the screen is ended."""
        pass

    def size_components(self, size: tuple[int, int]):
        """
        Adjust the size and position of components according to the screen size

        Specifications:
        - The buttons are in a row at the bottom of the screen,
          with a 16px margin between them, and 16px from the edge of the screen.
        - The image is centered above the buttons, with a 16px margin between them.
        """
        # Buttons
        self.flip_button.set_position((16, size[1] - 16 - self.flip_button.size[1]))
        self.rotate_button.set_position((
            self.flip_button.position[0] + self.flip_button.size[0] + 16,
            size[1] - 16 - self.rotate_button.size[1]
        ))
        self.swap_button.set_position((
            self.rotate_button.position[0] + self.rotate_button.size[0] + 16,
            size[1] - 16 - self.swap_button.size[1]
        ))
        self.filter_button.set_position((
            self.swap_button.position[0] + self.swap_button.size[0] + 16,
            size[1] - 16 - self.filter_button.size[1]
        ))

        # Image
        buttons_row_size = self.flip_button.size[0] + 16\
            + self.rotate_button.size[0] + 16\
            + self.swap_button.size[0] + 16\
            + self.filter_button.size[0]

        img_side_size = buttons_row_size
        max_height = size[1] - 16 - self.flip_button.size[1] - 16 - 16
        if max_height < img_side_size:
            img_side_size = max_height

        self.image.fit_size = img_side_size, img_side_size
        self.image.update_surface()

        position = (
            (16 + buttons_row_size + 16 - img_side_size) // 2,
            (size[1] - 16 - self.flip_button.size[1] - 16 - img_side_size) // 2,
        )
        self.image.set_position(position)

        self.logger.info("Updated components dimensions")
