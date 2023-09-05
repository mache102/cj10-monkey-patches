from __future__ import annotations

# For avoiding circular imports during type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main.engine import Engine

import abc
import pygame


class Screen(abc.ABC):
    """A screen that initialize components to be used by the engine."""

    @abc.abstractmethod
    def on_init(self, engine: Engine):
        """Called when the screen is initialized."""
        pass

    def on_event(self, engine: Engine, delta_time: float, event: pygame.event.Event):
        """Called when an event occurs."""
        pass

    def on_end(self, engine: Engine):
        """Called when the screen is ended."""
        pass


class ScreenManager:
    """A manager to manage screen"""

    screens: dict[str, Screen]
    next_screen: str | None
    curr_screen: str | None

    def __init__(self):
        self.screens = {}
        self.next_screen = None
        self.curr_screen = None

    def add_screen(self, name: str, screen: Screen):
        """Add a screen to the manager."""
        self.screens[name] = screen

    def get_curr_screen(self) -> Screen | None:
        """Get the current screen."""
        if self.curr_screen:
            return self.screens[self.curr_screen]
        return None

    def set_screen(self, name: str):
        """Set the current screen, actually delayed until end of current loop in engine."""
        self.next_screen = name

    def update(self, engine: Engine) -> bool:
        """
        Update the current screen

        Return true if screen is updated
        """
        if self.next_screen:
            if self.get_curr_screen():
                self.get_curr_screen().on_end(engine)
            self.curr_screen = self.next_screen
            self.next_screen = None
            self.get_curr_screen().on_init(engine)
            return True
        return False
