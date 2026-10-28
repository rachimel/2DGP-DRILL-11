"""Player model, state machine and rendering."""
from math import pi
from pathlib import Path

from transitions import Machine


class Boy:
    BASE_SIZE = 100
    GROUND_Y = 60
    WALK_SPEED = 100.0

    def __init__(self):
        self.x = 400.0
        self.direction = 1
        self.frame = 0
        self.frame_time = 0.0
        self.held = set()
        self.scale = 1.0
        self.image = None
        self.machine = Machine(model=self, states=['IDLE', 'WALK', 'SLEEP', 'AUTO_RUN'],
                               initial='IDLE', auto_transitions=False,
                               after_state_change='_reset_animation')
        self.machine.add_transition('rest', ['WALK', 'AUTO_RUN'], 'IDLE')
        self.machine.get_state('IDLE').add_callback('enter', '_enter_idle')
        self.machine.add_transition('start_walk', ['IDLE', 'SLEEP'], 'WALK')
        self.machine.add_transition('fall_asleep', 'IDLE', 'SLEEP')
        self.machine.add_transition('run_auto', ['IDLE', 'WALK'], 'AUTO_RUN')
        self._enter_idle()

    def _reset_animation(self):
        self.frame = 0
        self.frame_time = 0.0

    def _enter_idle(self):
        self.speed = 0.0
        self.idle_elapsed = 0.0

    def handle_events(self, events):
        changed = False
        pressed = set()
        for key, down in events:
            if down == (key in self.held):
                continue
            changed = True
            if down:
                self.held.add(key)
                pressed.add(key)
            else:
                self.held.discard(key)
        if pressed.intersection({'a', 'd'}) and self.state in ('IDLE', 'WALK'):
            self.direction = 1 if 'd' in pressed else -1
            self.run_auto()
            return
        if changed:
            self._sync_walk()

    def clear_inputs(self):
        self.held.clear()
        if self.state == 'WALK':
            self.rest()

    def _sync_walk(self):
        direction = int('right' in self.held) - int('left' in self.held)
        if direction:
            self.direction = direction
            if self.state in ('IDLE', 'SLEEP'):
                self.start_walk()
        elif self.state == 'WALK':
            self.rest()

    def _animate(self, dt, fps=8):
        total = self.frame_time + dt
        steps = int((total + 1e-12) * fps)
        self.frame = (self.frame + steps) % 8
        self.frame_time = max(0.0, total - steps / fps)

    def update(self, dt):
        if self.state == 'WALK':
            self.speed = self.WALK_SPEED
            self.x += self.direction * self.speed * dt
            self._animate(dt)

        elif self.state == 'IDLE':
            self.idle_elapsed += dt
            self._animate(dt)
            if self.idle_elapsed >= 5.0:
                self.fall_asleep()

        elif self.state == 'SLEEP':
            self._animate(dt, fps=2)

    def draw(self):
        import pico2d as p
        if self.image is None:
            self.image = p.load_image(str(Path(__file__).with_name('animation_sheet.png')))
        row = (101 if self.direction == 1 else 1) if self.state == 'WALK' else (301 if self.direction == 1 else 201)
        sleeping = self.state == 'SLEEP'
        angle = self.direction * pi / 2 if sleeping else 0.0
        y = self.GROUND_Y + (20 if sleeping else 37)
        self.image.clip_composite_draw(1 + self.frame * 100, row, 100, 100,
                                      angle, '', self.x, y, 100, 100)
