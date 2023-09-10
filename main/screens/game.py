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
from main.engine.text_rendering import (
    height_of_rendered_text, width_of_rendered_text
)
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
    game: 'GameScreen'

    def __init__(
        self,
        op_name: str,
        scrambled_image: ScrambledImage,
        scale: int = 1,
        size: tuple[int, int] = (50, 12),
        game: 'GameScreen' = None,
    ):
        super().__init__(op_name, scale=scale, size=size)
        self.scrambled_image = scrambled_image
        self.game = game


class FlipButton(ImageOpButton):
    """A flip button."""

    def __init__(self, scale: int, scrambled_image: ScrambledImage, game: 'GameScreen'):
        super().__init__("FLIP", scale=scale, scrambled_image=scrambled_image, game=game)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        image_ops.flip_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
        self.scrambled_image.update_surface()
        self.game.check_victory()

    def on_key_press(self, event: pygame.event.Event):
        """Called when the keyboard shortcut is pressed."""
        if event.key == pygame.K_q:
            image_ops.flip_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
            self.scrambled_image.update_surface()
            self.game.check_victory()


class RotateButton(ImageOpButton):
    """A rotate button."""

    def __init__(self, scale: int, scrambled_image: ScrambledImage, game: 'GameScreen'):
        super().__init__("ROTATE", scale=scale, scrambled_image=scrambled_image, game=game)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        image_ops.rotate_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
        self.scrambled_image.update_surface()
        self.game.check_victory()

    def on_key_press(self, event: pygame.event.Event):
        """Called when the keyboard shortcut is pressed."""
        if event.key == pygame.K_w:
            image_ops.rotate_tiles(self.scrambled_image.tile_arr, self.scrambled_image.selected_tile)
            self.scrambled_image.update_surface()
            self.game.check_victory()


class SwapButton(ImageOpButton):
    """A swap button."""

    def __init__(self, scale: int, scrambled_image: ScrambledImage, game: 'GameScreen'):
        super().__init__("SWAP", scale=scale, scrambled_image=scrambled_image, game=game)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        prev_tile = self.scrambled_image.prev_tile
        current_tile = self.scrambled_image.selected_tile
        if prev_tile != current_tile:
            image_ops.swap_tiles(self.scrambled_image.tile_arr, prev_tile, current_tile)
            self.scrambled_image.update_surface()
            self.game.check_victory()
            print("Swapped")


class NewPuzzleButton(components.LabeledButton):
    """Transitions from a solved puzzle to an unsolved puzzle, and solves the current one if unsolved."""

    puzzle: Optional[Puzzle] = None
    solving: bool = False
    solving_animation_time: float = 0.
    steps_remaining: list = None

    TIME_PER_STEP = 0.25

    def __init__(self, scale: int, scrambled_image: ScrambledImage, game: 'GameScreen'):
        super().__init__("NEW PUZZLE", scale=scale, size=(75, 12))
        self.scrambled_image = scrambled_image
        self.game = game

    def on_click(self, event: pygame.event.Event):
        """Solve, then generate a new puzzle on click."""
        if self.puzzle is not None and not self.solving:
            # Reset puzzle to untouched, start animating solution
            self.scrambled_image.tile_arr[:] = self.puzzle.puzzle_tiles
            self.solving = True
            self.steps_remaining = self.puzzle.puzzle_to_original
            self.label = "..."
            self.render_text()
            return

        puzzle = generate_puzzle(
            self.scrambled_image.tile_arr,
            difficulty=2,
        )
        self.scrambled_image.update_surface()
        self.puzzle = puzzle
        self.label = "SOLVE"
        self.render_text()

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
                    self.game.check_victory()  # debug
                    self.solving = False
                    self.puzzle = None
                    self.label = "NEW PUZZLE"
                    self.render_text()


class FadingAnnouncement(components.Text):
    """Displays a textual announcement over the game that fades after some time."""

    # Seconds to display the announcement
    display_for: float
    displayed_for: float = 0.0
    # Seconds over which the announcement fades before vanishing
    fade_over: float
    faded_over: float = 0.0
    fading: bool = False

    def __init__(
        self,
        text: str,
        display_for: float = 3.0,
        fade_over: float = 1.0,
        position: Optional[tuple[int, int]] = None,
        color: tuple[int, int, int] = (255, 0, 255),
        scale: int = 1,
        engine: 'Engine' = None,
    ):
        if position is None:
            # Default to display centered
            position = engine.display.get_size()
            text_size = width_of_rendered_text(text, scale), height_of_rendered_text(text, scale)
            position = position[0] // 2 - text_size[0] // 2, position[1] // 2 - text_size[1]

        super().__init__(text, position, color, scale)
        self.display_for = display_for
        self.fade_over = fade_over
        self.engine = engine

    def update(self, delta_time: float, events: list[pygame.event.Event]):
        """Slowly fade out the text after the configured time."""
        super().update(delta_time, events)

        if not self.fading:
            self.displayed_for += delta_time
            if self.displayed_for > self.display_for:
                self.fading = True
                delta_time = self.displayed_for - self.display_for

        if self.fading:
            self.faded_over += delta_time
            fade_percentage = self.faded_over / self.fade_over
            if fade_percentage <= 1.0:
                self.image.set_alpha(255 - int(fade_percentage * 255))
            else:
                self.engine.remove_sprite("announcements", self)


class BackButton(components.LabeledButton):
    """Goes back to puzzle selection screen"""

    def __init__(self, scale: int, game: 'GameScreen'):
        super().__init__('BACK', scale=scale)
        self.game = game

    def on_click(self, event: pygame.event.Event):
        """Sets the screen to the level screenpre-"""
        self.game.engine.set_screen("levels")


class GameScreen(Screen):
    """The game screen."""

    logger: logging.Logger
    engine: Engine

    image: ScrambledImage
    flip_button: FlipButton
    rotate_button: RotateButton
    swap_button: SwapButton
    reset_button: NewPuzzleButton

    SCALE: int = 3
    BUTTON_MARGIN: int = 4

    tile_size: int
    puzzle_no: int

    def __init__(self, puzzle_no: int, tile_size: int):
        self.puzzle_no = puzzle_no
        self.tile_size = tile_size

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game screen")
        self.engine = engine

        engine.background_color = (240, 240, 240)

        # Image
        engine.add_layer("image")

        scramble_config = ScrambleConfig(  # TODO: Use level configs
            tile_size=self.tile_size,
            path=Path(f"puzzle{self.puzzle_no}.png"),
            outline_thickness=1,
            outline_color=(0, 0, 0, 255),
        )
        self.image = ScrambledImage(scramble_config)

        engine.add_sprite("image", self.image)

        # Buttons
        engine.add_layer("buttons")

        self.flip_button = FlipButton(self.SCALE, self.image, self)
        self.rotate_button = RotateButton(self.SCALE, self.image, self)
        self.swap_button = SwapButton(self.SCALE, self.image, self)
        self.reset_button = NewPuzzleButton(self.SCALE, self.image, self)
        self.back_button = BackButton(self.SCALE, self)

        engine.add_sprite("buttons", self.flip_button)
        engine.add_sprite("buttons", self.rotate_button)
        engine.add_sprite("buttons", self.swap_button)
        engine.add_sprite("buttons", self.reset_button)
        engine.add_sprite("buttons", self.back_button)

        self.size_components(engine.display.get_size())

        engine.add_layer("announcements")

        self.logger.info("Initialized game screen")

    def on_event(self, engine: Engine, delta_time: float, events: list[pygame.event.Event]):
        """Called each frame with all new events."""
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.size_components((event.w, event.h))

    def check_victory(self):
        """Determine if the puzzle is solved, and if so display a victory text!"""
        if self.reset_button.puzzle and (self.image.tile_arr == self.reset_button.puzzle.original_tiles).all():
            print("WIN!")
            self.engine.add_sprite(
                "announcements",
                FadingAnnouncement(
                    "YOU WIN!",
                    engine=self.engine,
                    color=(50, 255, 50),
                    scale=self.SCALE + 3,
                ),
            )
            self.reset_button.solving = False
            self.reset_button.puzzle = None
            self.reset_button.label = "NEW PUZZLE"
            self.reset_button.render_text()

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

        width, height = size

        # Buttons
        self.flip_button.set_position((margin, height - margin - self.flip_button.size[1]))
        self.rotate_button.set_position((
            self.flip_button.position[0] + self.flip_button.size[0] + margin,
            height - margin - self.rotate_button.size[1]
        ))
        self.swap_button.set_position((
            self.rotate_button.position[0] + self.rotate_button.size[0] + margin,
            height - margin - self.swap_button.size[1]
        ))
        self.reset_button.set_position((
            self.swap_button.position[0] + self.swap_button.size[0] + margin,
            height - margin - self.reset_button.size[1]
        ))

        # Image
        buttons_row_size = (self.flip_button.size[0] + margin
                            + self.rotate_button.size[0] + margin
                            + self.swap_button.size[0] + margin
                            + self.reset_button.size[0])

        img_side_size = buttons_row_size
        max_height = height - margin - self.flip_button.size[1] - margin * 2
        if max_height < img_side_size:
            img_side_size = max_height

        self.image.fit_size = img_side_size, img_side_size
        self.image.update_surface()

        position = (
            (margin + buttons_row_size + margin - img_side_size) // 2,
            (height - margin - self.flip_button.size[1] - margin - img_side_size) // 2,
        )
        self.image.set_position(position)
        self.logger.info("Updated components dimensions")

        self.back_button.set_position((width - self.back_button.size[0] - 10, 10))
