import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pygame
from PIL import Image
from pydantic import BaseModel

from main import image_ops
from main.engine import Engine, Screen, components, utils
from main.engine.puzzle_generation import Puzzle, generate_puzzle
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
    # For swapping tiles
    prev_tile: tuple[int, int]
    selected_tile: tuple[int, int]
    fit_size: tuple[int, int]

    image_array: ImageArray
    select_array: ImageArray

    def __init__(self, scramble_config: ScrambleConfig):
        super().__init__()

        self.config = scramble_config

        # Open image array
        logo_png = Image.open(Path(__file__).parent.parent / 'data' / 'Images' / scramble_config.path)
        self.image_array = utils.add_alpha_to_arr(conv_pil_to_numpy(logo_png))
        self.fit_size = self.image_array.shape[:2]

        self.tile_arr = conv_img_arr_to_tile(self.image_array, self.config.tile_size)
        self.prev_tile = (0, 0)
        self.selected_tile = (0, 0)

        self.update_surface()

        self.logger = logging.getLogger(__name__)

    def on_click(self, event: pygame.event.Event):
        """Called when the image is clicked."""
        local_pos = event.pos[0] - self.position[0], event.pos[1] - self.position[1]

        self.logger.debug(f"Clicked tile at local pos {local_pos}")
        self.prev_tile = self.selected_tile
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

    def __init__(
        self,
        op_name: str,
        scrambled_image: ScrambledImage,
        scale: int = 1,
        size: tuple[int, int] = (50, 12),
    ):
        super().__init__(op_name, scale=scale, size=size)
        self.scrambled_image = scrambled_image


class FlipButton(ImageOpButton):
    """A flip button."""

    def __init__(self, scale: int, scrambled_image: ScrambledImage):
        super().__init__("FLIP", scale=scale, scrambled_image=scrambled_image)

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

    def __init__(self, scale: int, scrambled_image: ScrambledImage):
        super().__init__("ROTATE", scale=scale, scrambled_image=scrambled_image)

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

    def __init__(self, scale: int, scrambled_image: ScrambledImage):
        super().__init__("SWAP", scale=scale, scrambled_image=scrambled_image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        prev_tile = self.scrambled_image.prev_tile
        current_tile = self.scrambled_image.selected_tile
        if prev_tile != current_tile:
            image_ops.swap_tiles(self.scrambled_image.tile_arr, prev_tile, current_tile)
            self.scrambled_image.update_surface()
            print("Swapped")


class FilterButton(ImageOpButton):
    """A filter button."""

    def __init__(self, scale: int, scrambled_image: ScrambledImage):
        super().__init__("FILTER", scale=scale, scrambled_image=scrambled_image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Filtered")


class NewPuzzleButton(components.LabeledButton):
    """Transitions from a solved puzzle to an unsolved puzzle, and solves the current one if unsolved."""

    puzzle: Optional[Puzzle] = None
    solving: bool = False
    solving_animation_time: float = 0.
    steps_remaining: list = None

    TIME_PER_STEP = 0.25

    def __init__(self, scale: int, scrambled_image: ScrambledImage):
        super().__init__("RESET", scale=scale)
        self.scrambled_image = scrambled_image

    def on_click(self, event: pygame.event.Event):
        """Solve, then generate a new puzzle on click."""
        if self.puzzle is not None and not self.solving:
            # Reset puzzle to untouched, start animating solution
            self.scrambled_image.tile_arr[:] = self.puzzle.puzzle_tiles
            self.solving = True
            self.steps_remaining = self.puzzle.puzzle_to_original
            return

        puzzle = generate_puzzle(
            self.scrambled_image.tile_arr,
            difficulty=2,
        )
        self.scrambled_image.update_surface()
        self.puzzle = puzzle

    def update(self, delta_time: float, events: list[pygame.event.Event]):
        """Handle animating a puzzle solution."""
        super().update(delta_time, events)

        if self.solving:
            self.solving_animation_time += delta_time
            if self.solving_animation_time > self.TIME_PER_STEP:
                step_function, *args = self.steps_remaining.pop(0)
                if len(args) == 2:
                    step_function(self.scrambled_image.tile_arr, *args[0], **args[1])
                else:
                    step_function(self.scrambled_image.tile_arr, *args[0])
                self.scrambled_image.update_surface()
                self.solving_animation_time = 0

                if not self.steps_remaining:
                    self.solving = False
                    self.puzzle = None


class GameScreen(Screen):
    """The game screen."""

    logger: logging.Logger

    image: ScrambledImage
    flip_button: FlipButton
    rotate_button: RotateButton
    swap_button: SwapButton
    filter_button: FilterButton
    reset_button: NewPuzzleButton

    SCALE: int = 3
    BUTTON_MARGIN: int = 4

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game screen")

        engine.background_color = (240, 240, 240)

        # Image
        engine.add_layer("image")

        scramble_config = ScrambleConfig(  # TODO: Use level configs
            tile_size=50,
            path=Path("pydis_logo.png"),
            outline_thickness=1,
            outline_color=(0, 0, 0, 255),
        )
        self.image = ScrambledImage(scramble_config)

        engine.add_sprite("image", self.image)

        # Buttons
        engine.add_layer("buttons")

        self.flip_button = FlipButton(self.SCALE, self.image)
        self.rotate_button = RotateButton(self.SCALE, self.image)
        self.swap_button = SwapButton(self.SCALE, self.image)
        self.filter_button = FilterButton(self.SCALE, self.image)
        self.reset_button = NewPuzzleButton(self.SCALE, self.image)

        engine.add_sprite("buttons", self.flip_button)
        engine.add_sprite("buttons", self.rotate_button)
        engine.add_sprite("buttons", self.swap_button)
        engine.add_sprite("buttons", self.filter_button)
        engine.add_sprite("buttons", self.reset_button)

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
          with a 4px margin between them, and 4px from the edge of the screen.
        - The image is centered above the buttons, with a 4px margin between them.
        """
        margin = self.BUTTON_MARGIN * self.SCALE

        # Buttons
        self.flip_button.set_position((margin, size[1] - margin - self.flip_button.size[1]))
        self.rotate_button.set_position((
            self.flip_button.position[0] + self.flip_button.size[0] + margin,
            size[1] - margin - self.rotate_button.size[1]
        ))
        self.swap_button.set_position((
            self.rotate_button.position[0] + self.rotate_button.size[0] + margin,
            size[1] - margin - self.swap_button.size[1]
        ))
        self.filter_button.set_position((
            self.swap_button.position[0] + self.swap_button.size[0] + margin,
            size[1] - margin - self.filter_button.size[1]
        ))
        self.reset_button.set_position((
            self.filter_button.position[0] + self.filter_button.size[0] + margin,
            size[1] - margin - self.reset_button.size[1]
        ))

        # Image
        buttons_row_size = self.flip_button.size[0] + margin\
            + self.rotate_button.size[0] + margin\
            + self.swap_button.size[0] + margin\
            + self.filter_button.size[0] + margin\
            + self.reset_button.size[0]

        img_side_size = buttons_row_size
        max_height = size[1] - margin - self.flip_button.size[1] - margin - margin
        if max_height < img_side_size:
            img_side_size = max_height

        self.image.fit_size = img_side_size, img_side_size
        self.image.update_surface()

        position = (
            (margin + buttons_row_size + margin - img_side_size) // 2,
            (size[1] - margin - self.flip_button.size[1] - margin - img_side_size) // 2,
        )
        self.image.set_position(position)

        self.logger.info("Updated components dimensions")
