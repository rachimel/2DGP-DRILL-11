"""Drill 11 game loop. Run with the game2d Python environment."""
import pico2d as p


class Game:
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        p.open_canvas(self.WIDTH, self.HEIGHT, sync=True)
