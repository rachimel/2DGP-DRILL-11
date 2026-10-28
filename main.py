"""Drill 11 game loop. Run with the game2d Python environment."""
import pico2d as p


class Game:
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        p.open_canvas(self.WIDTH, self.HEIGHT, sync=True)
        self.running = True

    def run(self, max_frames=None):
        frames = 0
        try:
            while self.running and (max_frames is None or frames < max_frames):
                for event in p.get_events():
                    if event.type == p.SDL_QUIT or (event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE):
                        self.running = False
                p.clear_canvas()
                p.update_canvas()
                frames += 1
        finally:
            p.close_canvas()


if __name__ == '__main__':
    Game().run()
