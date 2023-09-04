from itertools import chain
from typing import Iterable

import numpy as np
import pygame

from main.type_aliases import ImageArray


def make_surface_rgba(array: ImageArray, scale: int = 1):
    """Returns the surface from a (w, h, 3 or 4) numpy array with per-pixel alpha, defaults to 255 if no alpha"""
    shape = array.shape
    if len(shape) != 3 or shape[2] not in (3, 4):
        raise ValueError("Array must be (w, h, 3 or 4) numpy array.")

    if scale != 1:
        array = np.repeat(np.repeat(array, scale, 1), scale, 0)

    # Create a surface the same width and height as array and with per-pixel alpha.
    surface = pygame.Surface(array.shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:, :, :3])

    # Copy the alpha part of array to the surface using a pixels-alpha view of the surface.
    surface_alpha = np.array(surface.get_view('A'), copy=False)
    surface_alpha[:, :] = array[:, :, 3] if array.shape[-1] == 4 else 255

    return surface


def flatten(iterable: Iterable[Iterable]) -> Iterable:
    """Convert a list of lists into one chained list"""
    yield from chain.from_iterable(iterable)
