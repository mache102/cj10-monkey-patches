import logging
import pygame
from main.engine import Engine, Screen, components


class FlipButton(components.LabeledButton):
    """A flip button."""

    def __init__(self):
        super().__init__("FLIP", size=(300, 50))

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Flipped")


class RotateButton(components.LabeledButton):
    """A rotate button."""

    def __init__(self):
        super().__init__("ROTATE", size=(300, 50))

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Rotated")


class SwapButton(components.LabeledButton):
    """A swap button."""

    def __init__(self):
        super().__init__("SWAP", size=(300, 50))

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Swapped")


class FilterButton(components.LabeledButton):
    """A filter button."""

    def __init__(self):
        super().__init__("FILTER", size=(300, 50))

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        print("Filtered")


class GameScreen(Screen):
    """The game screen."""

    logger: logging.Logger
    flip_button: FlipButton
    rotate_button: RotateButton
    swap_button: SwapButton
    filter_button: FilterButton

    SCALE: int = 4

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game screen")

        engine.add_layer("buttons", pygame.sprite.RenderUpdates())

        self.flip_button = FlipButton()
        self.rotate_button = RotateButton()
        self.swap_button = SwapButton()
        self.filter_button = FilterButton()

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
        """
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


        self.logger.info("Updated components dimensions")
