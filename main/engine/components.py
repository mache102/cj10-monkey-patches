import abc

import numpy as np
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
        return utils.make_image_rgba(self.image)

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

    def set_surface(self, image_array: ImageArray, stretch_to_fit: bool = False):
        """
        Set the surface of the component with an array of shape (height, width, 4).

        If stretch_to_fit is True, the image will be stretched to fit the component size.
        """
        if stretch_to_fit:
            image_array = utils.scale_arr(image_array, self.size)
        elif len(image_array.shape) != 3 or image_array.shape[:2] != self.size:
            raise ValueError(f"Surface size {image_array.shape[:2]} does not match component size {self.size}.")

        self.image = utils.make_surface_rgba(image_array)

    def set_9_slice_surface(self, image_array: ImageArray, border: tuple[int, int, int, int], scale: int = 1):
        """
        Use a 9-slice algorithm to create a surface from an image array.

        The image array should have a shape of (height, width, 4).

        The border should be a tuple of (top, right, bottom, left) border sizes.
        """
        # Scale the image and border
        image_array = utils.scale_arr(image_array, scale)
        border = tuple(b * scale for b in border)

        # Slice
        top_left = image_array[:border[0], :border[3]]
        top_right = image_array[:border[0], -border[1]:]
        bottom_left = image_array[-border[2]:, :border[3]]
        bottom_right = image_array[-border[2]:, -border[1]:]

        top = image_array[:border[0], border[3]:-border[1]]
        bottom = image_array[-border[2]:, border[3]:-border[1]]
        left = image_array[border[0]:-border[2], :border[3]]
        right = image_array[border[0]:-border[2], -border[1]:]

        center = image_array[border[0]:-border[2], border[3]:-border[1]]

        # Stretch top and bottom to fill self.size - border[1] - border[3]
        top = utils.stretch_arr(top, (border[0], self.size[1] - border[1] - border[3]))
        bottom = utils.stretch_arr(bottom, (border[2], self.size[1] - border[1] - border[3]))

        # Stretch left and right to fill self.size - border[0] - border[2]
        left = utils.stretch_arr(left, (self.size[0] - border[0] - border[2], border[3]))
        right = utils.stretch_arr(right, (self.size[0] - border[0] - border[2], border[1]))

        # Stretch center to fill self.size - border[0] - border[2], border[3] - border[1]
        center = utils.stretch_arr(
            center,
            (self.size[0] - border[0] - border[2], self.size[1] - border[1] - border[3]),
        )

        # Create the image array
        new_image = np.zeros((*self.size, 4), dtype=np.uint8)

        new_image[:border[0], :border[3]] = top_left
        new_image[:border[0], -border[1]:] = top_right
        new_image[-border[2]:, :border[3]] = bottom_left
        new_image[-border[2]:, -border[1]:] = bottom_right

        new_image[:border[0], border[3]:-border[1]] = top
        new_image[-border[2]:, border[3]:-border[1]] = bottom
        new_image[border[0]:-border[2], :border[3]] = left
        new_image[border[0]:-border[2], -border[1]:] = right

        new_image[border[0]:-border[2], border[3]:-border[1]] = center

        self.set_surface(new_image)

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
