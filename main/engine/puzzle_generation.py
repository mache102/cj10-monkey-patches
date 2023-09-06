
import random
from typing import Any, Literal, Optional

import main.image_ops as image_ops
from main.type_aliases import TileArray


class Puzzle:
    """Represents an image puzzle and it's solution strategy."""

    seed: int
    original_tiles: TileArray
    puzzle_tiles: TileArray
    # Format: callable, args, kwargs, does not include the required first argument of the tilearray
    puzzle_to_original: list[tuple[callable, tuple[Any]] | tuple[callable, tuple[Any], dict[str, Any]]]

    def __init__(
        self,
        seed: int,
        original_tiles: TileArray,
        puzzle_tiles: TileArray,
        puzzle_to_original: list,
    ):
        self.seed = seed
        self.original_tiles = original_tiles
        self.puzzle_tiles = puzzle_tiles
        self.puzzle_to_original = puzzle_to_original


def generate_puzzle(
        tiles: TileArray,
        difficulty: int = 1,
        seed: Optional[int] = None,
):
    """Generate a new scrambled image puzzle from the source image"""
    if seed is None:
        seed = random.randint(1, 2**64)

    rng = random.Random(seed)

    # scale up difficulty (number of operations, each tick adds more possibilities too)

    difficulty *= 4

    original = tiles.copy()
    # Overwrite original image array
    puzzled = tiles
    auto_solve_steps = []

    for step in range(difficulty):
        target_tile = (rng.randint(0, puzzled.shape[0]-1), rng.randint(0, puzzled.shape[1]-1))

        match rng.randint(0, 5):
            case 0:
                tile_2_x = rng.randint(0, puzzled.shape[0]-1)
                tile_2_y = rng.randint(0, puzzled.shape[1]-1)

                image_ops.swap_tiles(puzzled, target_tile, (tile_2_x, tile_2_y))

                auto_solve_steps.append((image_ops.swap_tiles, ((tile_2_x, tile_2_y), target_tile)))

            case 1:
                image_ops.flip_tiles(puzzled, target_tile, axis='horizontal')
                auto_solve_steps.append(
                    (image_ops.flip_tiles, (target_tile,), {"axis": "horizontal"})
                )

            case 2:
                image_ops.flip_tiles(puzzled, target_tile, axis='vertical')
                auto_solve_steps.append(
                    (image_ops.flip_tiles, (target_tile,), {"axis": "vertical"})
                )
            case 3:
                rotation: Literal[90, 180, 270] = rng.choice([90, 180, 270])
                image_ops.rotate_tiles(puzzled, target_tile, rotation=rotation)
                auto_solve_steps.append(
                    (image_ops.rotate_tiles, (target_tile,), {"rotation": 360-rotation})
                )

    return Puzzle(
        seed=seed,
        original_tiles=original,
        puzzle_tiles=puzzled.copy(),
        puzzle_to_original=list(reversed(auto_solve_steps)),
    )
