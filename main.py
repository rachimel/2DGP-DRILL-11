"""Drill 11 game loop. Run with the game2d Python environment."""
from time import perf_counter

import pico2d as p
import pico2d.pico2d as canvas

from grass import Grass


class Game:
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        p.open_canvas(self.WIDTH, self.HEIGHT, sync=True)
        if not canvas.renderer:
            canvas.renderer = canvas.SDL_CreateRenderer(canvas.window, -1, canvas.SDL_RENDERER_SOFTWARE)
        if not canvas.renderer:
            p.close_canvas()
            raise RuntimeError('SDL renderer could not be created')
        self.running = True
        self.grass = Grass()

    def update(self, dt):
        self.last_dt = dt

    def run(self, max_frames=None):
        frames = 0
        previous = perf_counter()
        try:
            while self.running and (max_frames is None or frames < max_frames):
                for event in p.get_events():
                    if event.type == p.SDL_QUIT or (event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE):
                        self.running = False
                now = perf_counter()
                dt = now - previous
                previous = now
                self.update(dt)
                p.clear_canvas()
                self.grass.draw()
                p.update_canvas()
                frames += 1
        finally:
            p.close_canvas()


if __name__ == '__main__':
    Game().run()
