from typing import Iterable

import numpy as np
import pygame

from main.typing import ImageArray


def make_surface_rgba(array: ImageArray) -> pygame.Surface:
    """Returns the surface from a (w, h, 4) numpy array with per-pixel alpha"""
    array = arr2d_swap_xy(array)
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array must be (w, h, 4) numpy array.")

    # Create a surface the same width and height as array and with per-pixel alpha.
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:, :, :3])

    # Copy the alpha part of array to the surface using a pixels-alpha view of the surface.
    surface_alpha = np.array(surface.get_view('A'), copy=False)
    surface_alpha[:, :] = array[:, :, 3]

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

    array = arr2d_swap_xy(array)
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
    for sub_iterable in iterable:
        yield from sub_iterable


def scale_arr(array: ImageArray, scale: int) -> ImageArray:
    """Scales an array by a given factor."""
    return np.repeat(np.repeat(array, scale, axis=0), scale, axis=1)


def stretch_arr(array: ImageArray, new_size: tuple[int, int]) -> ImageArray:
    """
    Stretches an array to a new size.

    The new size should be a tuple of (height, width).
    """
    # Kind of a cheat by using pygame
    surface = make_surface_rgba(array)
    surface = pygame.transform.scale(surface, (new_size[1], new_size[0]))
    return make_image_rgba(surface)
