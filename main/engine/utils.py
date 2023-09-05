from itertools import chain
from typing import Iterable

import numpy as np
import pygame

from main.type_aliases import ImageArray


def make_surface_rgba(array: ImageArray, scale: int = 1) -> pygame.Surface:
    """Returns the surface from a (w, h, 4) numpy array with per-pixel alpha"""
    shape = array.shape
    if len(shape) != 3 or shape[2] not in (3, 4):
        raise ValueError("Array must be (w, h, 3 or 4) numpy array.")

    scale_arr(array, scale)

    # Create a surface the same width and height as array and with per-pixel alpha.
    surface = pygame.Surface(array.shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:, :, :3])

    # Copy the alpha part of array to the surface using a pixels-alpha view of the surface.
    surface_alpha = np.array(surface.get_view('A'), copy=False)
    surface_alpha[:, :] = array[:, :, 3] if array.shape[-1] == 4 else 255

    return surface


def make_image_rgba(surface: pygame.Surface) -> ImageArray:
    """Returns a (w, h, 4) numpy array from a surface with per-pixel alpha"""
    shape = surface.get_size() + (4,)

    # Create a numpy array with the same width and height as surface and with per-pixel alpha.
    array = np.empty(shape, dtype=np.uint8)

    # Copy the rgb part of surface to the new array.
    array[:, :, :3] = pygame.surfarray.pixels3d(surface)

    # Copy the alpha part of surface to the array using a pixels-alpha view of the surface.
    surface_alpha = np.array(surface.get_view('A'), copy=False)
    array[:, :, 3] = surface_alpha

    return array


def merge_images(top: ImageArray, bottom: ImageArray) -> ImageArray:
    """
    Merge two images together by multiplying with alpha channel then summing.

    `top` image will be placed on top of `bottom` image.
    """
    if top.shape != bottom.shape:
        raise ValueError("Images must be the same shape.")

    # Multiply top image by alpha channel
    top[:, :, :3] *= top[:, :, 3:] / 255

    # Sum the two images
    return top + bottom


def vec2d_swap_xy(vec: tuple[int, int]):
    """Swap the x and y components of a 2d vector."""
    return vec[1], vec[0]


def arr2d_swap_xy(arr: ImageArray):
    """Swap the x and y axes of a 2d numpy array."""
    return arr.swapaxes(0, 1)


def flatten(iterable: Iterable[Iterable]) -> Iterable:
    """Convert a list of lists into one chained list"""
    yield from chain.from_iterable(iterable)


def scale_arr(array: ImageArray, scale: int) -> ImageArray:
    """Scales an array uniformly on x y axis by a given factor."""
    return np.repeat(np.repeat(array, scale, axis=0), scale, axis=1)


def stretch_arr(array: ImageArray, new_size: tuple[int, int]) -> ImageArray:
    """
    Stretches an array to a new size.

    The new size should be a tuple of (width, height).
    """
    # Kind of a cheat by using pygame
    surface = make_surface_rgba(array)
    surface = pygame.transform.scale(surface, new_size)
    return make_image_rgba(surface)
