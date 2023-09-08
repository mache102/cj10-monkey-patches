import abc
from pathlib import Path

import numpy as np
import pygame
from PIL import Image as PILImage

from main.engine import text_rendering, utils
from main.image_ops import conv_pil_to_numpy
from main.type_aliases import ImageArray


class BaseComponent(abc.ABC, pygame.sprite.DirtySprite):
    """A sprite that can be drawn by the engine."""

    is_down: bool
    is_hovered: bool
    scale: float

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((0, 0)).convert_alpha()
        self.rect = self.image.get_rect()

        self.is_down = False
        self.is_hovered = False

    @property
    def position(self) -> tuple[int, int]:
        """The (x, y) top left position of the component."""
        return self.rect.x, self.rect.y

    @property
    def size(self) -> tuple[int, int]:
        """The (width, height) size of the component."""
        return self.rect.width, self.rect.height

    @property
    def center(self) -> tuple[int, int]:
        """The (x, y) center position of the component."""
        return self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2

    @property
    def surface(self) -> ImageArray:
        """The surface of the component."""
        return utils.make_image_rgba(self.image)

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        pass

    def on_key_press(self, event: pygame.event.Event):
        """Called when a key is pressed."""
        pass

    def on_mouse_enter(self, event: pygame.event.Event):
        """Called when the mouse enters the component."""
        pass

    def on_mouse_leave(self, event: pygame.event.Event):
        """Called when the mouse leaves the component."""
        pass

    def set_position(self, position: tuple[int, int]):
        """Set the (x, y) top left position of the component."""
        self.rect.x, self.rect.y = position

    def set_size(self, size: tuple[int, int]):
        """Set the (width, height) size of the component."""
        self.rect.width, self.rect.height = size

    def set_surface(self, image_array: ImageArray, scale: int = 1, stretch_to_fit: bool = False):
        """
        Set the surface of the component with an array of shape (width, height, 4).

        If stretch_to_fit is True, the image will be stretched to fit the component size.
        It will also scale up the image_array with scale, so make sure image_array.shape * scale == self.size.
        """
        scaled_image_size = image_array.shape[:2][0] * scale, image_array.shape[:2][1] * scale
        if stretch_to_fit:
            image_array = utils.scale_arr(image_array, self.size)
        elif len(image_array.shape) != 3 or scaled_image_size != self.size:
            raise ValueError(f"Surface size {scaled_image_size} does not match component size {self.size}.")

        self.image = utils.make_surface_rgba(image_array)

    def set_9_slice_surface(self, image_array: ImageArray, border: tuple[int, int, int, int], scale: int = 1):
        """
        Use a 9-slice algorithm to create a surface from an image array.

        The image array should have a shape of (width, height, 4).

        The border should be a tuple of (top, right, bottom, left) border sizes.
        It will also scale up the image_array with scale, so make sure image_array.shape * scale == self.size.
        """
        # Scale the image and border
        image_array = utils.scale_arr(image_array, scale)
        border = tuple(b * scale for b in border)

        # Slice with the border of (top, right, bottom, left)
        top, right, bottom, left = border
        top_left = image_array[:left, :top]
        top_right = image_array[-right:, :top]
        bottom_left = image_array[:left, -bottom:]
        bottom_right = image_array[-right:, -bottom:]
        top_center = image_array[left:-right, :top]
        bottom_center = image_array[left:-right, -bottom:]
        left_center = image_array[:left, top:-bottom]
        right_center = image_array[-right:, top:-bottom]
        center = image_array[left:-right, top:-bottom]

        # Stretch to fit
        top_center = utils.stretch_arr(top_center, (self.size[0] - left - right, top))
        bottom_center = utils.stretch_arr(bottom_center, (self.size[0] - left - right, bottom))
        left_center = utils.stretch_arr(left_center, (left, self.size[1] - top - bottom))
        right_center = utils.stretch_arr(right_center, (right, self.size[1] - top - bottom))
        center = utils.stretch_arr(center, (self.size[0] - left - right, self.size[1] - top - bottom))

        # Merge
        new_image = np.zeros((self.size[0], self.size[1], 4), dtype=np.uint8)

        new_image[:left, :top] = top_left
        new_image[-right:, :top] = top_right
        new_image[:left, -bottom:] = bottom_left
        new_image[-right:, -bottom:] = bottom_right
        new_image[left:-right, :top] = top_center
        new_image[left:-right, -bottom:] = bottom_center
        new_image[:left, top:-bottom] = left_center
        new_image[-right:, top:-bottom] = right_center
        new_image[left:-right, top:-bottom] = center

        self.set_surface(new_image)

    def set_text(
        self,
        text: str,
        position: tuple[int, int] = (0, 0),
        color: tuple[int, int, int] = (255, 0, 255),
        scale: int = 1
    ):
        """Set the text on top of the component."""
        text_rendering.render_on_surface(
            text,
            self.image,
            coords=position,
            color=color,
            scale=scale,
        )

    def update(self, delta_time: float, events: list[pygame.event.Event]):
        """Update the component."""
        for event in events:
            # mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.is_down = True
            # mouse click release
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_down:
                    self.is_down = False
                    self.on_click(event)
            # mouse movement
            elif event.type == pygame.MOUSEMOTION:
                if self.is_down and not self.rect.collidepoint(event.pos):
                    self.is_down = False

                if self.rect.collidepoint(event.pos):
                    if not self.is_hovered:
                        self.is_hovered = True
                        self.on_mouse_enter(event)
                else:
                    if self.is_hovered:
                        self.is_hovered = False
                        self.on_mouse_leave(event)
            # key press
            elif event.type == pygame.KEYDOWN:
                self.on_key_press(event)


class Text(BaseComponent):
    """A text component"""

    def __init__(
        self,
        text: str,
        position: tuple[int, int] = (0, 0),
        color: tuple[int, int, int] = (255, 0, 255),
        scale: int = 1
    ):
        super().__init__()

        text_surface = text_rendering.render_to_surface(text.upper(), color=color, scale=scale)
        self.image = text_surface
        self.rect = text_surface.get_rect()
        self.rect.move_ip(position[1], position[0])


class Image(BaseComponent):
    """An image component"""

    def __init__(self, image_array: ImageArray, position: tuple[int, int] = (0, 0)):
        super().__init__()

        test_img = utils.make_surface_rgba(image_array, scale=1)
        self.image = test_img
        self.rect = test_img.get_rect()
        self.rect.move_ip(*position)


button_image_path = PILImage.open(Path(__file__).parent.parent / 'data' / 'Images' / 'button.png')
button_image = utils.add_alpha_to_arr(conv_pil_to_numpy(button_image_path))


class LabeledButton(BaseComponent):
    """A labeled button."""

    label: str
    scale: int

    def __init__(
        self,
        label: str,
        scale: int = 1,
        position: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (50, 12),
    ):
        super().__init__()
        # width, height
        self.set_size((size[0] * scale, size[1] * scale))

        # x, y
        self.set_position(position)

        self.label = label
        self.scale = scale

        self.render_text()

    @property
    def scaled_size(self) -> tuple[int, int]:
        """The (width, height) size of the component, scaled by the scale."""
        return self.size[0] * self.scale, self.size[1] * self.scale

    def render_text(self):
        """Render the text."""
        self.set_9_slice_surface(button_image, border=(4, 4, 4, 4), scale=self.scale)

        offset = text_rendering.width_of_rendered_text(self.label, scale=self.scale)

        self.set_text(
            self.label,
            position=((self.size[0] - offset) // 2, 2 * self.scale),
            color=(0, 0, 0),
            scale=self.scale,
        )

    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        pass
