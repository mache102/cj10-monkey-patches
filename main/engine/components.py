import abc

import pygame

from main.engine import text_rendering
from main.engine import utils
from main.typing import ImageArray


class BaseComponent(abc.ABC, pygame.sprite.DirtySprite):
    """A sprite that can be drawn by the engine."""

    is_down: bool

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((0, 0)).convert_alpha()
        self.rect = self.image.get_rect()

        self.is_down = False

    @property
    def position(self) -> tuple[int, int]:
        """The (y, x) top left position of the component."""
        return self.rect.y, self.rect.x

    @property
    def size(self) -> tuple[int, int]:
        """The (height, width) size of the component."""
        return self.rect.height, self.rect.width

    @property
    def center(self) -> tuple[int, int]:
        """The (y, x) center position of the component."""
        return self.position[1] + self.size[1] // 2, self.position[0] + self.size[0] // 2

    @property
    def surface(self) -> ImageArray:
        """The surface of the component."""
        return utils.arr2d_swap_xy(pygame.surfarray.pixels3d(self.image))

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        pass

    def set_position(self, position: tuple[int, int]):
        """Set the (y, x) top left position of the component."""
        self.rect.y = position[0]
        self.rect.x = position[1]

    def set_size(self, size: tuple[int, int]):
        """Set the (height, width) size of the component."""
        self.rect.height = size[0]
        self.rect.width = size[1]

    def set_surface(self, image_array: ImageArray):
        """
        Set the surface of the component with an array of shape (height, width, 4).

        If rgba is True, the surface will be converted to an alpha surface.
        """
        if len(image_array.shape) != 3 or image_array.shape[:2] != self.size:
            raise ValueError(f"Surface size {image_array.shape[:2]} does not match component size {self.size}.")

        self.image = utils.make_surface_rgba(utils.arr2d_swap_xy(image_array))

    def set_text(
        self,
        text: str,
        position: tuple[int, int] = (0, 0),
        color: tuple[int, int, int] = (255, 0, 255),
        scale: int = 3
    ):
        """Set the text on top of the component."""
        text_rendering.render_on_surface(
            text,
            self.image,
            coords=(position[1], position[0]),
            color=color,
            scale=scale,
        )

    def update(self, delta_time: float, events: list[pygame.event.Event]):
        """Update the component."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.is_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_down:
                    self.is_down = False
                    self.on_click(event)
            elif event.type == pygame.MOUSEMOTION:
                if self.is_down and not self.rect.collidepoint(event.pos):
                    self.is_down = False


class Text(BaseComponent):
    """A text component"""

    def __init__(
        self,
        text: str,
        position: tuple[int, int] = (0, 0),
        color: tuple[int, int, int] = (255, 0, 255),
        scale: int = 3
    ):
        super().__init__()

        text_surface = text_rendering.render_to_surface(text.upper(), color=color, scale=scale)
        self.image = text_surface
        self.rect = text_surface.get_rect()
        self.rect.move_ip(position[1], position[0])
