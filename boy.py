"""Player model, state machine and rendering."""
from math import isfinite, pi
from pathlib import Path
import json

from transitions import Machine


class Boy:
    SPRITE_BOUNDS = json.loads(Path(__file__).with_name('sprite_bounds.json').read_text(encoding='utf-8'))
    SCREEN_WIDTH = 800
    BASE_SIZE = 100
    GROUND_Y = 60
    WALK_SPEED = 100.0
    AUTO_START_SPEED = 100.0
    AUTO_ACCEL = 100.0
    AUTO_DECEL = 200.0
    AUTO_DURATION = 5.0

    def __init__(self):
        self.x = 400.0
        self.direction = 1
        self.frame = 0
        self.frame_time = 0.0
        self.held = set()
        self.blocked_walk = set()
        self.scale = 1.0
        self.image = None
        self.machine = Machine(model=self, states=['IDLE', 'WALK', 'SLEEP', 'AUTO_RUN'],
                               initial='IDLE', auto_transitions=False,
                               after_state_change='_reset_animation')
        self.machine.add_transition('rest', ['WALK', 'AUTO_RUN'], 'IDLE')
        self.machine.get_state('IDLE').add_callback('enter', '_enter_idle')
        self.machine.add_transition('start_walk', ['IDLE', 'SLEEP'], 'WALK')
        self.machine.add_transition('fall_asleep', 'IDLE', 'SLEEP')
        self.machine.add_transition('run_auto', ['IDLE', 'WALK', 'SLEEP'], 'AUTO_RUN')
        self.machine.get_state('AUTO_RUN').add_callback('enter', '_enter_auto')
        self.machine.get_state('AUTO_RUN').add_callback('exit', '_exit_auto')
        self._enter_idle()

    def _reset_animation(self):
        self.frame = 0
        self.frame_time = 0.0

    def _enter_idle(self):
        self.speed = 0.0
        self.idle_elapsed = 0.0

    def _enter_auto(self):
        self.speed = self.AUTO_START_SPEED
        self.auto_elapsed = 0.0
        self.braking = False
        self.scale = 2.0
        self._reset_animation()
        self._constrain()

    def _exit_auto(self):
        self.scale = 1.0
        self.blocked_walk = self.held.intersection({'left', 'right'})

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
                self.blocked_walk.discard(key)
        if pressed.intersection({'a', 'd'}) and self.state in ('IDLE', 'WALK', 'SLEEP'):
            self.direction = 1 if 'd' in pressed else -1
            self.run_auto()
            return
        if changed:
            self._sync_walk()

    def clear_inputs(self):
        self.held.clear()
        self.blocked_walk.clear()
        if self.state == 'WALK':
            self.rest()

    def _sync_walk(self):
        if self.state == 'AUTO_RUN':
            return
        active = self.held - self.blocked_walk
        direction = int('right' in active) - int('left' in active)
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

    @property
    def remaining_auto_time(self):
        return max(0.0, self.AUTO_DURATION - self.auto_elapsed)

    @property
    def stopping_time(self):
        return self.speed / self.AUTO_DECEL

    def _advance_auto(self, dt):
        # Split a frame at the acceleration/braking boundary and at standstill.
        while dt > 1e-12:
            if not self.braking:
                switch_in = max(0.0, (self.remaining_auto_time - self.stopping_time)
                                / (1 + self.AUTO_ACCEL / self.AUTO_DECEL))
                if switch_in <= 1e-12:
                    self.braking = True
                    continue
                step = min(dt, switch_in, 0.125 - self.frame_time)
                distance = self.speed * step + 0.5 * self.AUTO_ACCEL * step * step
                self.speed += self.AUTO_ACCEL * step
            else:
                step = min(dt, 0.125 - self.frame_time,
                           self.stopping_time if self.speed > 1e-9 else self.remaining_auto_time)
                distance = self.speed * step - 0.5 * self.AUTO_DECEL * step * step if self.speed > 1e-9 else 0.0
                self.speed = max(0.0, self.speed - self.AUTO_DECEL * step)
                if self.speed < 1e-9:
                    self.speed = 0.0
            self._move_auto(distance)
            self.auto_elapsed += step
            self._animate(step)
            self._constrain()
            dt -= step
            if self.auto_elapsed >= self.AUTO_DURATION and self.speed == 0.0:
                self.rest()
                if dt > 0:
                    self.update(dt)
                return

    @property
    def horizontal_bounds(self):
        left, top, right, bottom = self.SPRITE_BOUNDS[str(self.sprite_row)][self.frame]
        visible_width = bottom - top if self.state == 'SLEEP' else right - left
        half = visible_width * self.scale / 2
        return half, self.SCREEN_WIDTH - half

    def _move_auto(self, distance):
        # Fold the travelled position across both walls; preserve overshoot.
        left, right = self.horizontal_bounds
        span = right - left
        phase = (self.x - left + self.direction * distance) % (2 * span)
        self.x = left + (phase if phase <= span else 2 * span - phase)
        if phase == 0:
            self.direction = 1
        elif phase == span:
            self.direction = -1
        elif phase > span:
            self.direction *= -1

    def _constrain(self):
        left, right = self.horizontal_bounds
        self.x = min(right, max(left, self.x))
        if self.state == 'AUTO_RUN' and self.x <= left and self.direction < 0:
            self.direction = 1
        elif self.state == 'AUTO_RUN' and self.x >= right and self.direction > 0:
            self.direction = -1

    def update(self, dt):
        if not isfinite(dt) or dt < 0:
            raise ValueError('Frame delta must be finite and nonnegative')
        if self.state == 'WALK':
            self.speed = self.WALK_SPEED
            self.x += self.direction * self.speed * dt
            self._animate(dt)

        elif self.state == 'AUTO_RUN':
            self._advance_auto(dt)
        elif self.state == 'IDLE':
            step = min(dt, max(0.0, 5.0 - self.idle_elapsed))
            self.idle_elapsed += step
            self._animate(step)
            if self.idle_elapsed >= 5.0:
                self.fall_asleep()
                self._animate(dt - step, fps=2)

        elif self.state == 'SLEEP':
            self._animate(dt, fps=2)

        self._constrain()

    def draw(self):
        import pico2d as p
        if self.image is None:
            self.image = p.load_image(str(Path(__file__).with_name('animation_sheet.png')))
        row = self.sprite_row
        left, top, right, bottom = self.SPRITE_BOUNDS[str(row)][self.frame]
        sleeping = self.state == 'SLEEP'
        angle = self.direction * pi / 2 if sleeping else 0.0
        width = (right - left) * self.scale
        height = (bottom - top) * self.scale
        visible_height = width if sleeping else height
        y = self.GROUND_Y + visible_height / 2
        self.image.clip_composite_draw(1 + self.frame * 100 + left, row + 100 - bottom,
                                      right - left, bottom - top,
                                      angle, '', self.x, y, width, height)

    @property
    def sprite_row(self):
        if self.state in ('WALK', 'AUTO_RUN'):
            return 101 if self.direction == 1 else 1
        return 301 if self.direction == 1 else 201
