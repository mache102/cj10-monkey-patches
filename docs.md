Start game by executing
```bash
python -m main.main
```

`main/data/images`:  
A directory for storing the images to be used for levels  

`main/data/asciifont.py`:
python dict for storing the pixel art of the ascii characters

`main/engine/__init__.py`:
The game engine, engine settings, and sprite layer storage.
    EngineSettings:
    fps, vsync option, display

    Layer:
    "a layer of sprites to render"

    Engine:
    A tile and sprite based engine
    Includes options to add and remove layers by name
    The sprites and layers are updated according to a clock and the provided fps
    Then the layers are redrawn

    Screens can also be modified
    mainloop() starts the engine


`main/engine/components.py`:
Various components that can be drawn by the engine
    BaseComponent:
    The fundamental base class for all components
    Includes pos, size, surface, image/text setting,
    and pygame event handling

    TextComponent:
    text component

    ImageComponent:
    image component

    LabeledButton:
    A button component with text

    RefrigeratorComponent:
    a ham sandwich

`main/engine/screen.py`:
A screen manager for components

`main/engine/text_rendering.py`:
Render the custom font to a surface

`main/engine/utils.py`:
Some image utils
- surface -> rgba
- image -> rgba
- merge images
- vec/arr swap xy
- flatten, scale, stretch
- outline for tile selection
- add alpha to rgb

`main/screens/game.py`:
Game screen, game image (BaseComponent),
and image operation buttons (rotate, flip, etc.)


`main/screens/test.py`:
test screen and test button

`main/image_ops.py`:
all tile arr image operations
- pil to numpy
- image arr to tile arr
- rotate
- flip
- swap
- filter

`main/type_aliases.py`:
type aliases for simplicity
