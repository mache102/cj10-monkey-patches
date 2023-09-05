import os
from typing import Optional

import numpy as np
import pygame
import pygame.locals

from main.data.asciifont import LETTER_ASCII as RAW_LETTER_ASCII
from main.engine import utils
from main.type_aliases import ImageArray

LETTER_ASCII = {}
for letter, raw_data in RAW_LETTER_ASCII.items():
    # Purge leading and trailing newlines, but not spaces since some letters begin with spaces
    raw_data = raw_data.strip("\n")
    # Remove trailing spaces from individual lines
    raw_lines = [i.rstrip(" ") for i in raw_data.split("\n")]
    raw_data = "\n".join(raw_lines)
    # Replace sentinel for intentional empty lines now that we're done processing
    data = raw_data.replace(".", " ")

    LETTER_ASCII[letter] = data

# Letter: (width, height)
LETTER_DIMENSIONS = {
    letter: (
        max(len(i) for i in letter_data.split("\n")),
        len(letter_data.split("\n")),
    ) for letter, letter_data in LETTER_ASCII.items()
}

LINE_HEIGHT = max(height for letter, (width, height) in LETTER_DIMENSIONS.items())
LINE_SPACING = 1
LETTER_SPACING = 1


LETTER_NDARRAYS = {}
for letter, letter_data in LETTER_ASCII.items():
    LETTER_NDARRAYS[letter] = np.zeros((LETTER_DIMENSIONS[letter][0], LINE_HEIGHT), dtype=np.bool_)
    # if LETTER_DIMENSIONS[letter][1] < LINE_HEIGHT:
    #     y_offset = LINE_HEIGHT - LETTER_DIMENSIONS[letter][1]
    # else:
    #     y_offset = 0

    for y, line in enumerate(letter_data.split("\n"), start=0):
        for x, pixel in enumerate(line):
            LETTER_NDARRAYS[letter][x, y] = pixel != " "


def render_ascii_art(string: str, max_width: Optional[int] = None) -> str:
    """Render a string into ascii art using our custom font"""
    if not max_width:
        max_width = os.get_terminal_size()[0]

    # Wrap text
    lines = []
    current_width = 0
    letters_to_concatenate = []
    for letter in string:
        if letter not in LETTER_ASCII:
            raise ValueError("Font does not contain character '%s'" % letter)

        letter_width = LETTER_DIMENSIONS[letter][0]
        if letter_width + current_width + LETTER_SPACING < max_width:
            letters_to_concatenate.append(letter)
            current_width += letter_width + LETTER_SPACING
            continue

        letters_to_render = letters_to_concatenate
        letters_to_concatenate = [letter]

        lines.append(render_letters(letters_to_render))
        current_width = letter_width

    # Render final line
    if letters_to_concatenate:
        lines.append(render_letters(letters_to_concatenate))

    output = []
    for text_line in lines:
        line_out = []
        # To render, we need to read y -> x order. Data is stored in x -> y order.
        for terminal_line in text_line.swapaxes(0, 1):
            line_out.append(''.join(" #"[bool(i)] for i in terminal_line))
        output.append("\n".join(line_out))

    return ("\n"*(LINE_SPACING + 1)).join(output)


def render_on_surface(
    letters: str,
    surface: pygame.Surface,
    coords: tuple[int, int] = (0, 0),
    color: tuple[int, int, int] = (255, 0, 255),
    scale: int = 1,
):
    """Render a string of text onto the provided pygame surface using our ascii font and numpy"""
    # TODO: generalize text wrapping
    rendered_array = render_letters(list(letters))

    if scale != 1:
        rendered_array = np.repeat(np.repeat(rendered_array, scale, 1), scale, 0)

    surface_array = pygame.surfarray.pixels3d(surface)
    # expand our render mask to have a replicated "color" dimension
    render_mask = np.expand_dims(rendered_array, 2)
    # Replicate color across a 3d array of where we'll be rendering
    color_base = np.broadcast_to(np.array(color, dtype=np.uint8), (*rendered_array.shape, surface_array.shape[-1]))
    # AND with mask to do the drawing
    rendered_font_image_array = color_base * render_mask

    if rendered_array.shape[0] > surface_array.shape[0]:
        raise ValueError("Cannot render text: destination surface is not wide enough: %s < %s"
                         % (surface_array.shape[0], rendered_array.shape[0]))
    if rendered_array.shape[1] > surface_array.shape[1]:
        raise ValueError("Cannot render text: destination surface is not tall enough: %s < %s"
                         % (surface_array.shape[1], rendered_array.shape[1]))

    # Paste drawn text onto the destination surface
    np.copyto(
        surface_array[
            coords[0]:coords[0]+rendered_array.shape[0],
            coords[1]:coords[1]+rendered_array.shape[1],
            :
        ],
        rendered_font_image_array,
        where=render_mask,
    )
    del surface_array
    # update per-pixel alphas too
    # this is done separately in pygame for some reason
    # We don't do blending for the moment. Set to opaque according to mask.
    alphas_array = pygame.surfarray.pixels_alpha(surface)
    np.copyto(
        alphas_array[
            coords[0]:coords[0] + rendered_array.shape[0],
            coords[1]:coords[1] + rendered_array.shape[1],
        ],
        255,
        where=rendered_array,
    )

    return pygame.Rect(*coords, *rendered_array.shape)


def render_to_surface(text: str, color: tuple[int, int, int] = (255, 0, 255), scale: int = 1) -> pygame.Surface:
    """Render a given string onto a new pygame surface using our ascii font"""
    rendered_array = render_letters(text)
    surface = pygame.Surface((rendered_array.shape[0]*scale, rendered_array.shape[1]*scale), pygame.locals.SRCALPHA)
    render_on_surface(text, surface, color=color, scale=scale)
    return surface


def render_to_image_array(text: str, color: tuple[int, int, int] = (255, 0, 255), scale: int = 1) -> ImageArray:
    """Render a given string onto a new image array using our ascii font"""
    surface = render_to_surface(text, color=color, scale=scale)
    return pygame.surfarray.pixels3d(surface)


def render_letters(letters: list[str]) -> np.ndarray:
    """Render a list of letters to a numpy array of bool pixels."""
    spacing_array = np.zeros((LETTER_SPACING, LINE_HEIGHT), dtype=np.bool_)

    letter_arrays = list(utils.flatten((LETTER_NDARRAYS[letter], spacing_array) for letter in letters))

    render_array = np.concatenate(letter_arrays, axis=0, dtype=np.bool_)

    return render_array


def width_of_rendered_text(text: str, scale: int = 1) -> int:
    """Compute the width in dots that a given string will render with"""
    return (sum(LETTER_NDARRAYS[i].shape[0] for i in text) + LETTER_SPACING * len(text)) * scale


if __name__ == '__main__':
    print(render_ascii_art("ABCDEF"))
