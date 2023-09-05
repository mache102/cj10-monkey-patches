import logging

import pygame
from pydantic import BaseModel, Field

from main.engine.screen import Screen, ScreenManager


class EngineSettings(BaseModel):
    """Settings for the engine."""

    fps: int = Field(60)
    display: int = Field(0)
    vsync: bool = Field(False)


class Layer(pygame.sprite.RenderUpdates):
    """A layer of sprites to render."""

    priority: int

    def __init__(self, priority: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.priority = priority


class Engine:
    """A tile and sprite based game engine."""

    display: pygame.SurfaceType
    running: bool = False
    logger: logging.Logger
    clock: pygame.time.Clock
    settings: EngineSettings

    _layers: dict[str, Layer]  # name: layer
    screen_man: ScreenManager

    def __init__(self, settings: EngineSettings = EngineSettings()):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Starting engine!")

        self.settings = settings

        # Provide a list of desktops (for fullscreen, use display.Info() instead)
        display_info = pygame.display.get_desktop_sizes()
        self.logger.info("Available displays: %s", display_info)

        selected_display_size = display_info[settings.display]
        self.logger.info("Selected display: %s", selected_display_size)

        # For testing and debugging, default to 2/3 size
        window_size = (selected_display_size[0] / 3 * 2), (selected_display_size[1] / 3 * 2)
        self.logger.info("Creating a window with size %s", window_size)

        self.display = pygame.display.set_mode(window_size, flags=pygame.RESIZABLE, vsync=settings.vsync)

        # Do not pass fps here, as this clock is multi-use
        self.clock = pygame.time.Clock()

        self._layers = {}
        self.screen_man = ScreenManager()

    @property
    def layers(self) -> list[tuple[str, Layer]]:
        """A list of (name, layer) for the engine's render layers in priority sorted order"""
        return sorted(self._layers.items(), key=lambda item: item[1].priority)

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

        # Generate a priority if none is provided
        if priority is None:
            if len(self.layers) == 0:
                priority = 0
            else:
                priority = self.layers[-1][1].priority + 1

        if name in self._layers:
            raise ValueError("Duplicate layer name")

        self._layers[name] = Layer(priority=priority, *layer)

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
            self.logger.debug(event)
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.VIDEORESIZE:
                window_size = (event.w, event.h)
                self.logger.info("Updating a window with size %s", window_size)
                self.display = pygame.display.set_mode(window_size, flags=pygame.RESIZABLE, vsync=self.settings.vsync)

        delta_time = self.clock.tick(self.settings.fps) / 1000  # in seconds

        self.screen_man.get_curr_screen().on_event(self, delta_time, events)

        for name, layer in self.layers:
            self.logger.debug("Updating layer %s", name)
            layer.update(delta_time, events)

    def draw(self) -> list[pygame.Rect]:
        """Move all sprites and rerender all layers."""
        self.display.fill((0, 255, 0))

        dirty_rects = []
        for name, layer in self.layers:
            self.logger.debug("Drawing layer %s", name)
            dirty_rects.extend(layer.draw(self.display))

        pygame.display.update()
        return dirty_rects

    def set_screen(self, name: str):
        """Set the screen"""
        self.screen_man.set_screen(name)

    def add_screen(self, name: str, screen: Screen):
        """Add a screen"""
        self.screen_man.add_screen(name, screen)

    def mainloop(self, init_screen: str):
        """Start the engine."""
        self.running = True

        # First screen init
        self.screen_man.set_screen(init_screen)
        self._layers.clear()
        if self.screen_man.update(self):
            self.logger.info(f"Updated screen to {repr(self.screen_man.curr_screen)}")

        while self.running:
            self.update(pygame.event.get())
            dirty_rects = self.draw()
            pygame.display.update(dirty_rects)

            if self.screen_man.next_screen:
                self._layers.clear()
            if self.screen_man.update(self):
                self.logger.info(f"Updated screen to {repr(self.screen_man.curr_screen)}")

        del self.display
        pygame.quit()
