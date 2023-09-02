import logging

import pygame


class Engine:
    """A tile and sprite based game engine."""

    display: pygame.SurfaceType
    running: bool = False
    _layers: dict[str, pygame.sprite.RenderUpdates]
    _layer_priorities = list[tuple[int, str]]
    logger: logging.Logger
    clock: pygame.time.Clock
    fps: int = 60

    def __init__(self):
        self.logger = logging.getLogger("engine")
        self.logger.info("Starting engine!")

        # Provide a list of desktops (for fullscreen, use display.Info() instead)
        display_info = pygame.display.get_desktop_sizes()
        self.logger.info("Available displays: %s", display_info)

        selected_display_size = display_info[0]
        self.logger.info("Selected display: %s", selected_display_size)

        # For testing and debugging, default to 2/3 size
        window_size = (selected_display_size[0] / 3 * 2), (selected_display_size[1] / 3 * 2)
        self.logger.info("Creating a window with size %s", window_size)

        self.display = pygame.display.set_mode(window_size, vsync=True)

        # Do not pass fps here, as this clock is multi-use
        self.clock = pygame.time.Clock()

        self._layers = {}
        self._layer_priorities = []

    @property
    def layers(self):
        """A list of (name, layer) for the engine's render layers in priority sorted order"""
        return ((name, self._layers[name]) for _, name in self._layer_priorities)

    def add_layer(
        self,
        name: str,
        layer: pygame.sprite.RenderUpdates,
        priority: int | None = None,
    ):
        """
        Add a rendering layer to the display engine, by name. Use the name to add or remove sprites later.

        The default for priority is below all previously assigned layers.
        """
        self.logger.debug("Adding new layer '%s' at priority %s", name, "default" if priority is None else priority)
        if priority is None:
            priority = max(self._layer_priorities.values(), default=0) + 1

        if name in self._layers.keys():
            raise ValueError("Duplicate layer name")

        self._layers[name] = layer

        self._layer_priorities.append((priority, name))
        self._layer_priorities.sort()

    def add_sprite(self, layer: str, *sprites: pygame.sprite.DirtySprite):
        """Add a sprite to a render layer."""
        if layer not in self._layers:
            raise ValueError("Cannot add sprite to nonexistent layer %s", layer)

        self._layers[layer].add(*sprites)

    def remove_sprite(self, layer: str, *sprites: pygame.sprite.DirtySprite):
        """Add a sprite to a render layer."""
        if layer not in self._layers:
            raise ValueError("Cannot remove a sprite from nonexistent layer %s", layer)

        self._layers[layer].remove(*sprites)

    def update(self, events: list[pygame.Event]):
        """Update all sprites and layers with events that have occurred since last call."""
        for event in events:
            print(event)
            if event.type == pygame.QUIT:
                self.running = False

        tick_time = self.clock.tick(self.fps) / 1000
        for name, layer in self.layers:
            self.logger.debug("Updating layer %s", name)
            layer.update(tick_time, events)

    def draw(self) -> list[pygame.Rect]:
        """Move all sprites and rerender all layers."""
        self.display.fill((0, 255, 0))

        dirty_rects = []
        for name, layer in self.layers:
            self.logger.debug("Drawing layer %s", name)
            dirty_rects.extend(layer.draw(self.display))

        return dirty_rects

    def mainloop(self):
        """Start the engine."""
        self.running = True

        while self.running:
            self.update(pygame.event.get())
            dirty_rects = self.draw()
            pygame.display.update(dirty_rects)

        del self.display
        pygame.quit()
