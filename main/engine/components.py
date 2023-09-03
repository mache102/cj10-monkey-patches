import abc
import numpy
import numpy.typing
import pygame


class BaseComponent(abc.ABC, pygame.sprite.DirtySprite):
    """A sprite that can be drawn by the engine."""

    is_down: bool

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((0, 0)).convert_alpha()
        self.rect = self.image.get_rect()

        self.is_down = False

    @property
    def position(self) -> tuple[int, int]:
        """The x coordinate of the component."""
        return self.rect.x, self.rect.y

    @property
    def size(self) -> tuple[int, int]:
        """The width of the component."""
        return self.rect.width, self.rect.height

    @property
    def center(self) -> tuple[int, int]:
        """The center of the component."""
        return self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2

    @property
    def surface(self) -> numpy.typing.NDArray[numpy.uint8]:
        """The surface of the component."""
        return pygame.surfarray.pixels3d(self.image)

    @abc.abstractmethod
    def on_click(self, event: pygame.event.Event):
        """Called when the button is clicked."""
        pass

    def set_position(self, position: tuple[int, int]):
        """Set the position of the component."""
        self.rect.x = position[0]
        self.rect.y = position[1]

    def set_size(self, size: tuple[int, int]):
        """Set the size of the component."""
        self.rect.width = size[0]
        self.rect.height = size[1]

    def set_surface(self, surface: numpy.typing.NDArray[numpy.uint8]):
        """
        Set the surface of the component.

        If rgba is True, the surface will be converted to an alpha surface.
        """
        if surface.shape[:2] != self.size:
            raise ValueError(f"Surface size {surface.shape[:2]} does not match component size {self.size}.")

        self.image = make_surface_rgba(surface)

    def update(self, delta_time: float, events: list[pygame.event.Event]):
        """Update the component."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.is_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_down:
                    self.is_down = False
                    self.on_click(event)
            elif event.type == pygame.MOUSEMOTION:
                if self.is_down and not self.rect.collidepoint(event.pos):
                    self.is_down = False


def make_surface_rgba(array: numpy.typing.NDArray[numpy.uint8]):
    """Returns a surface made from a [w, h, 4] numpy array with per-pixel alpha"""
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array not RGBA")

    # Create a surface the same width and height as array and with per-pixel alpha.
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:, :, 0:3])

    # Copy the alpha part of array to the surface using a pixels-alpha view of the surface.
    surface_alpha = numpy.array(surface.get_view('A'), copy=False)
    surface_alpha[:, :] = array[:, :, 3]

    return surface
