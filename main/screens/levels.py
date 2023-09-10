import logging

import pygame

from main.engine import Engine, Screen, components


class LevelButton(components.LabeledButton):
    """A level button"""

    engine: Engine
    level: int

    def __init__(self, engine: Engine, level: int, *args, **kwargs):
        super().__init__(f"LEVEL {level}", *args, **kwargs)
        self.level = level
        self.engine = engine

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.engine.set_screen("game")


class BackButton(components.LabeledButton):
    """The back button"""

    engine: Engine

    def __init__(self, engine: Engine, *args, **kwargs):
        super().__init__("BACK", *args, **kwargs)
        self.engine = engine

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.engine.set_screen("main_menu")


class LevelsScreen(Screen):
    """The level screen"""

    level_buttons: list[LevelButton]
    back_button: BackButton

    LEVEL_COUNT: int = 10  # TODO: Load from file
    SCALE: int = 3
    BUTTON_SIZE: tuple[int, int] = (70, 12)
    BUTTON_MARGIN: int = 4

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing levels")

        engine.background_color = (240, 240, 240)

        # Buttons
        engine.add_layer("buttons", pygame.sprite.RenderUpdates())

        self.level_buttons = []
        for level in range(self.LEVEL_COUNT):
            self.level_buttons.append(
                LevelButton(
                    engine,
                    level,
                    scale=self.SCALE,
                    size=self.BUTTON_SIZE,
                )
            )
            engine.add_sprite("buttons", self.level_buttons[-1])

        self.back_button = BackButton(engine, scale=self.SCALE, size=self.BUTTON_SIZE)
        engine.add_sprite("buttons", self.back_button)

        self.size_components(engine.display.get_size())

        self.logger.info("Initialized levels screen")

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
        - back button is located at top left, with a 4px margin from edges
        """
        margin = self.BUTTON_MARGIN * self.SCALE

        # Buttons
        button_width = max(
            *[button.size[0] for button in self.level_buttons],
        )

        button_height = max(
            *[button.size[1] for button in self.level_buttons],
        )

        button_stack_height = (
            len(self.level_buttons) * button_height + (len(self.level_buttons) - 1) * margin
        )

        button_stack_y = size[1] // 2 - button_stack_height // 2

        for i, button in enumerate(self.level_buttons):
            button.set_position((size[0] // 2 - button_width // 2, button_stack_y + i * (button_height + margin)))

        self.back_button.set_position((margin, margin))

        self.logger.info("Updated components dimensions")
