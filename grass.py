"""Ground rendering; resource paths are independent of the working directory."""
from pathlib import Path

import pico2d as p


class Grass:
    TOP = 60

    def __init__(self):
        self.image = p.load_image(str(Path(__file__).with_name('grass.png')))

    def draw(self):
        self.image.draw(400, self.TOP / 2, 800, self.TOP)
