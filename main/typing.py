import numpy as np
import numpy.typing as npt

# 8 bit int array of shape (height, width, channel count)
ImageArray = npt.NDArray[np.uint8]

# 8 bit int array of shape (tiled height, tiled width, tile height, tile width, channel count)
TileArray = npt.NDArray[np.uint8]
