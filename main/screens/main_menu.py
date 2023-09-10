import logging

import pygame

from main.engine import Engine, Screen, components


class MainMenuButton(components.LabeledButton):
    """A button for the main menu."""

    engine: Engine

    def __init__(
        self,
        label: str,
        engine: Engine,
        scale: int = 1,
        size: tuple[int, int] = (50, 12),
    ):
        super().__init__(label, scale=scale, size=size)
        self.engine = engine


class StartButton(MainMenuButton):
    """The start button."""

    def __init__(self, *args, **kwargs):
        super().__init__("START", *args, **kwargs)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.engine.set_screen("levels")


class CreditsButton(MainMenuButton):
    """The settings button."""

    def __init__(self, *args, **kwargs):
        super().__init__("CREDITS", *args, **kwargs)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.engine.set_screen("credits")


class QuitButton(MainMenuButton):
    """The quit button."""

    def __init__(self, *args, **kwargs):
        super().__init__("QUIT", *args, **kwargs)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.engine.running = False


class MainMenuScreen(Screen):
    """The main menu screen"""

    start_button: StartButton
    credits_button: CreditsButton
    quit_button: QuitButton

    SCALE: int = 3
    BUTTON_SIZE: tuple[int, int] = (70, 12)
    BUTTON_MARGIN: int = 4

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing main menu")

        engine.background_color = (240, 240, 240)

        # Buttons
        engine.add_layer("buttons")

        self.start_button = StartButton(engine, scale=self.SCALE, size=self.BUTTON_SIZE)
        self.credits_button = CreditsButton(engine, scale=self.SCALE, size=self.BUTTON_SIZE)
        self.quit_button = QuitButton(engine, scale=self.SCALE, size=self.BUTTON_SIZE)

        engine.add_sprite("buttons", self.start_button)
        engine.add_sprite("buttons", self.credits_button)
        engine.add_sprite("buttons", self.quit_button)

        self.size_components(engine.display.get_size())

        self.logger.info("Initialized main menu screen")

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
        - buttons are centered in a vertical stack, with a 4px margin between them.
        """
        margin = self.BUTTON_MARGIN * self.SCALE

        # Buttons
        button_width = max(
            self.start_button.size[0],
            self.credits_button.size[0],
            self.quit_button.size[0],
        )

        button_height = max(
            self.start_button.size[1],
            self.credits_button.size[1],
            self.quit_button.size[1],
        )

        button_x = (size[0] - button_width) // 2
        button_y = (size[1] - 3 * button_height - 2 * margin) // 2

        self.start_button.set_position((button_x, button_y))
        self.credits_button.set_position((button_x, button_y + button_height + margin))
        self.quit_button.set_position((button_x, button_y + 2 * button_height + 2 * margin))

        self.logger.info("Updated components dimensions")
