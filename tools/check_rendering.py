"""Offscreen SDL rendering and game-loop integration checks.

Run from the repository root: python tools/check_rendering.py
Writes actual framebuffer PNGs to validation/; does not capture the desktop.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import ctypes
import os
import struct
import sys
import zlib

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pico2d as p
import pico2d.pico2d as canvas
from boy import Boy
from main import Game


def save_frame(path):
    width, height = Game.WIDTH, Game.HEIGHT
    pixels = (ctypes.c_ubyte * (width * height * 4))()
    result = canvas.SDL_RenderReadPixels(canvas.renderer, None, canvas.SDL_PIXELFORMAT_ABGR8888, pixels, width * 4)
    if result != 0:
        raise RuntimeError(canvas.SDL_GetError())
    data = bytes(pixels)
    rows = b''.join(b'\x00' + data[y * width * 4:(y + 1) * width * 4] for y in range(height))

    def chunk(name, payload):
        return struct.pack('!I', len(payload)) + name + payload + struct.pack('!I', zlib.crc32(name + payload))

    header = struct.pack('!IIBBBBB', width, height, 8, 6, 0, 0, 0)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def run():
    output = ROOT / 'validation'
    output.mkdir(exist_ok=True)
    game = Game()
    try:
        for name in ['idle_right', 'walk_left', 'sleep_right', 'sleep_left', 'auto_right', 'auto_boundary_left']:
            boy = Boy()
            if name == 'walk_left':
                boy.handle_events([('left', True)])
                boy.update(.25)
            elif name.startswith('sleep'):
                boy.direction = -1 if name.endswith('left') else 1
                boy.update(5.5)
            elif name.startswith('auto'):
                boy.x = 50 if name.endswith('left') else 400
                boy.handle_events([('d', True)])
            p.clear_canvas()
            game.grass.draw()
            boy.draw()
            save_frame(output / f'{name}.png')
    finally:
        p.close_canvas()

    game = Game()
    events = [[SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_d)],
              [SimpleNamespace(type=p.SDL_KEYUP, key=p.SDLK_d)], []]
    with patch('main.p.get_events', side_effect=events), patch('main.perf_counter', side_effect=[0, .125, .25, .375]):
        game.run(max_frames=3)
    assert game.boy.state == 'AUTO_RUN'
    assert game.boy.auto_elapsed == .375
    assert game.boy.frame == 3
    game = Game()
    with patch('main.p.get_events', return_value=[SimpleNamespace(type=p.SDL_QUIT)]):
        game.run(max_frames=3)
    assert not game.running
    print('PASS: six actual SDL framebuffer images; key-down/up dispatch; timed update; quit cleanup')


if __name__ == '__main__':
    run()
