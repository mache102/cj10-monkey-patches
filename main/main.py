import logging

import pygame

from main.engine import Engine
from main.engine.text_rendering import LETTER_ASCII

# TODO: Remove this, this is just for testing
from main.engine import components
from main.engine import text_rendering

logging.basicConfig()

pygame.init()


# TODO: Remove this, this is just for testing
class TestButton(components.BaseComponent):
    """A count button."""

    count: int = 0

    def __init__(self):
        super().__init__()
        # height, width
        self.set_size((50, 200))

        # y, x
        self.set_position((100, 100))

        self.image = pygame.Surface(self.size[::-1], pygame.locals.SRCALPHA)

        self.render_text()

    def render_text(self):
        """Render the text."""
        # Erase our image
        self.image.fill((255, 255, 255))

        offset = text_rendering.width_of_rendered_text(str(self.count), scale=4)

        self.set_text(
            str(self.count),
            position=(10, self.size[1] - offset),
            color=(0, 0, 0),
            scale=4,
        )

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        self.count += 1
        print(self.count)
        self.render_text()


if __name__ == "__main__":
    engine = Engine()

    engine.add_layer("test-widgets", pygame.sprite.RenderUpdates())

    test_text = components.Text(''.join(LETTER_ASCII))
    engine.add_sprite("test-widgets", test_text)

    quick_fox_text = components.Text("The quick brown fox jumps over the lazy road-toad!")
    quick_fox_text.set_position((
        quick_fox_text.position[0] + quick_fox_text.rect.height + 18,
        quick_fox_text.position[1],
    ))
    engine.add_sprite("test-widgets", quick_fox_text)

    engine.add_sprite("test-widgets", TestButton())

    engine.mainloop()
