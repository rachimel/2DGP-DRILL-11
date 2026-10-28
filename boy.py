"""Player model, state machine and rendering."""
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
                               initial='IDLE', auto_transitions=False)
        self.machine.add_transition('rest', ['WALK', 'AUTO_RUN'], 'IDLE')
        self.machine.get_state('IDLE').add_callback('enter', '_enter_idle')
        self.machine.add_transition('start_walk', 'IDLE', 'WALK')
        self._enter_idle()

    def _enter_idle(self):
        self.speed = 0.0

    def handle_events(self, events):
        changed = False
        for key, down in events:
            if down == (key in self.held):
                continue
            changed = True
            if down:
                self.held.add(key)
            else:
                self.held.discard(key)
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
            if self.state == 'IDLE':
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
            self._animate(dt)

    def draw(self):
        import pico2d as p
        if self.image is None:
            self.image = p.load_image(str(Path(__file__).with_name('animation_sheet.png')))
        row = (101 if self.direction == 1 else 1) if self.state == 'WALK' else (301 if self.direction == 1 else 201)
        self.image.clip_draw(1 + self.frame * 100, row, 100, 100,
                             self.x, self.GROUND_Y + 50, 100, 100)
