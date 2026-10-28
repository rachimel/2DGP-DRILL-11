"""Ground rendering; resource paths are independent of the working directory."""
from pathlib import Path

import pico2d as p


class Grass:
    TOP = 60

    def __init__(self):
        self.image = p.load_image(str(Path(__file__).with_name('grass.png')))

    def draw(self):
        # Native 802x62 image has a 1px side border and 2px transparent top.
        # Its actual grass surface is therefore y=60, matching Boy.GROUND_Y.
        self.image.draw(400, 31, 802, 62)
