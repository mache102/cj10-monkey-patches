import logging

import pygame

from main.engine import Engine, Screen, components


class BackButton(components.LabeledButton):
    """The back button"""

    engine: Engine

    def __init__(self, engine: Engine, *args, **kwargs):
        super().__init__("BACK", *args, **kwargs)
        self.engine = engine

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.engine.set_screen("main_menu")


class CreditsScreen(Screen):
    """The credits screen"""

    credits_texts: list[components.Text | None]

    SCALE: int = 3
    TEXT: str = """
        Credits

        This is a game made for the Python Discord Code Jam 10
        By Team - The Monkey Patches

        Team Members - Discord / GitHub Names:
        segtwo / mache102
        Licken / LioQing
        Bast / bast0006
        Stickie / FieryIceStickie
    """
    BUTTON_SIZE: tuple[int, int] = (70, 12)
    TEXT_MARGIN: int = 4

    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing credits")

        engine.background_color = (240, 240, 240)

        # Credits
        engine.add_layer("credits", pygame.sprite.RenderUpdates())
        engine.add_layer("buttons", pygame.sprite.RenderUpdates())

        self.credits_texts = []
        for line in self.TEXT.upper().splitlines()[1:]:
            line = line.strip()
            if line == "":
                self.credits_texts.append(None)
                continue

            self.credits_texts.append(
                components.Text(
                    line,
                    scale=self.SCALE,
                    color=(0, 0, 0),
                )
            )
            engine.add_sprite("credits", self.credits_texts[-1])

        self.back_button = BackButton(engine, scale=self.SCALE, size=self.BUTTON_SIZE)
        engine.add_sprite("buttons", self.back_button)

        self.size_components(engine.display.get_size())

        self.logger.info("Initialized credits screen")

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
        - credit texts are centered in a vertical stack, with a 4px margin between them.
        """
        margin = self.TEXT_MARGIN * self.SCALE

        # Credits
        text_height = sum(
            text.size[1] if text is not None else self.credits_texts[0].size[1]
            for text in self.credits_texts
        ) + margin * (len(self.credits_texts) - 1)

        # Center the text
        center_x = size[0] // 2
        text_y = (size[1] - text_height) // 2

        for text in self.credits_texts:
            if text is not None:
                text_x = center_x - text.size[0] // 2
                text.set_position((text_x, text_y))
                text_y += text.size[1] + margin
            else:
                text_y += self.credits_texts[0].size[1] + margin

        # Back button
        self.back_button.set_position((margin, margin))

        self.logger.info("Updated components dimensions")
