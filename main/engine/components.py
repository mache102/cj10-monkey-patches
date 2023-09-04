import abc

import pygame

from main.engine.utils import arr2d_swap_xy, make_surface_rgba
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
        return arr2d_swap_xy(pygame.surfarray.pixels3d(self.image))

    @abc.abstractmethod
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

        self.image = make_surface_rgba(arr2d_swap_xy(image_array))

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
