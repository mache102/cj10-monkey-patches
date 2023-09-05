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
                 rotation: Literal[90, 180, 270] = 90) -> NoReturn:
    """Rotates tiles by rotation degrees counter-clockwise"""
    *indices, = zip(*tile_pos)
    # tile_arr[*indices] is an array of tiles,
    # so axes=(1, 2) ensures that the tiles are being rotated
    tile_arr[*indices] = np.rot90(tile_arr[*indices], k=rotation // 90, axes=(1, 2))


def flip_tiles(tile_arr: TileArray,
               *tile_pos: tuple[int, int],
               axis: Literal['horizontal', 'vertical'] = 'horizontal') -> NoReturn:
    """Flips tiles either horizontally or vertically"""
    *indices, = zip(*tile_pos)
    tile_arr[*indices] = np.flip(tile_arr[*indices], axis=1 if axis == 'vertical' else 2)


if __name__ == '__main__':
    pass
