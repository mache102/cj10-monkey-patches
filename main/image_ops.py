from typing import Literal, NoReturn

import numpy as np
from PIL import Image

from .type_aliases import ImageArray, TileArray


def conv_pil_to_numpy(img: Image) -> ImageArray:
    """Convert pillow image to a numpy array of (width, height)"""
    return np.array(img).swapaxes(0, 1)


def conv_img_arr_to_tile(image_arr: ImageArray, tile_size: int) -> TileArray:
    """
    Converts an image array into an array of tiles for image operations

    Note: Tiles should be square
    """
    width, height, channel_count = image_arr.shape
    # Check that the tile dimensions fit the image
    if width % tile_size or height % tile_size:
        raise ValueError(
            f'Tile of size {tile_size} does not fit with image of shape {(width, height)}'
        )
    return image_arr.reshape(
        width // tile_size, tile_size,
        height // tile_size, tile_size,
        channel_count
    ).swapaxes(1, 2)


def rotate_tiles(tile_arr: TileArray,
                 *tile_pos: tuple[int, int],
                 rotation: Literal[90, 180, 270] = 90) -> None:
    """
    Rotates tiles by rotation degrees counter-clockwise

    Tile positions are given by (row index, column index)
    """
    *indices, = zip(*tile_pos)
    # tile_arr[*indices] is an array of tiles,
    # so axes=(1, 2) ensures that the tiles are being rotated
    tile_arr[*indices] = np.rot90(tile_arr[*indices], k=rotation // 90, axes=(1, 2))


def flip_tiles(tile_arr: TileArray,
               *tile_pos: tuple[int, int],
               axis: Literal['horizontal', 'vertical'] = 'horizontal') -> None:
    """
    Flips tiles either horizontally or vertically

    Tile positions are given by (row index, column index)
    """
    *indices, = zip(*tile_pos)
    tile_arr[*indices] = np.flip(tile_arr[*indices], axis=1 if axis == 'vertical' else 2)

def swap_tiles(tile_arr: TileArray,
               tile1_pos: tuple[int, int],
               tile2_pos: tuple[int, int]) -> None:
    """
    Swaps the positions of two tiles

    Tile positions are given by (row index, column index)
    """
    temp_tile = tile_arr[tile1_pos].copy()
    tile_arr[tile1_pos] = tile_arr[tile2_pos]
    tile_arr[tile2_pos] = temp_tile


def apply_filter_to_tiles(tile_arr: TileArray,
                         *tile_pos: tuple[int, int],
                         grayscale: bool = False,
                         filter_color: tuple[int, int, int],
                         filter_strength: float = 1.0) -> None:
    """Applies a filter to a set of tiles"""

    if grayscale:
        # this ignores the filter color and strength
        *indices, = zip(*tile_pos)
        tile_arr[*indices] = np.mean(tile_arr[*indices], axis=3, keepdims=True)
        return

    # Im going for iteration here for readability
    for pos in tile_pos:
        tile = tile_arr[pos]
        
        filtered_tile = tile + (np.array(filter_color) * filter_strength)
        filtered_tile = np.clip(filtered_tile, 0, 255)
        tile_arr[pos] = filtered_tile


if __name__ == '__main__':
    pass
