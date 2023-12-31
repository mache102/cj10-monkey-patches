import numpy as np
import numpy.typing as npt

# 8 bit int array of shape (width, height, channel count)
ImageArray = npt.NDArray[np.uint8]

# 8 bit int array of shape (tiled width, tiled height, tile width, tile height, channel count)
TileArray = npt.NDArray[np.uint8]
