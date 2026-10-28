"""Player model, state machine and rendering."""
from pathlib import Path


class Boy:
    BASE_SIZE = 100
    GROUND_Y = 60

    def __init__(self):
        self.x = 400.0
        self.direction = 1
        self.frame = 0
        self.scale = 1.0
        self.image = None

    def draw(self):
        import pico2d as p
        if self.image is None:
            self.image = p.load_image(str(Path(__file__).with_name('animation_sheet.png')))
        row = 301 if self.direction == 1 else 201
        self.image.clip_draw(1 + self.frame * 100, row, 100, 100,
                             self.x, self.GROUND_Y + 50, 100, 100)
