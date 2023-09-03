from pathlib import Path
from typing import Literal, NoReturn

import numpy as np
import numpy.typing as npt
from PIL import Image

# 8 bit int array of shape (height, width, channel count)
ImageArray = npt.NDArray[np.uint8]
# 8 bit int array of shape (tiled height, tiled width, tile height, tile width, channel count)
TileArray = npt.NDArray[np.uint8]


def get_img_arr(image_path: Path) -> ImageArray:
    """Get the image data from the specified path and put it into a numpy array"""
    return np.array(Image.open(image_path))


def conv_img_arr_to_tile(image_arr: ImageArray, tile_size: int) -> TileArray:
    """
    Converts an image array into an array of tiles for image operations

    Note: Tiles should be square
    """
    height, width, channel_count = image_arr.shape
    # Check that the tile dimensions fit the image
    if height % tile_size or width % tile_size:
        raise ValueError(
            f'Tile of size {tile_size} does not fit with image of shape {(width, height)}'
        )
    return image_arr.reshape(
        height // tile_size, tile_size,
        width // tile_size, tile_size,
        channel_count
    ).swapaxes(1, 2)


def rotate_tiles(tile_arr: TileArray,
                 *tile_pos: tuple[int, int],
                 rotation: Literal[90, 180, 270] = 90) -> NoReturn:
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
               axis: Literal['horizontal', 'vertical'] = 'horizontal') -> NoReturn:
    """
    Flips tiles either horizontally or vertically

    Tile positions are given by (row index, column index)
    """
    *indices, = zip(*tile_pos)
    tile_arr[*indices] = np.flip(tile_arr[*indices], axis=1 if axis == 'vertical' else 2)
