"""Behaviour checks without opening a graphics window."""
import unittest
from itertools import permutations
from pathlib import Path
import re

from boy import Boy


class PlayerTests(unittest.TestCase):
    def test_same_frame_auto_priority_is_independent_of_event_order(self):
        for keys in permutations(['left', 'right', 'a', 'd']):
            boy = Boy()
            boy.handle_events([(key, True) for key in keys])
            self.assertEqual((boy.state, boy.direction), ('AUTO_RUN', 1))

    def test_walking_chord_release_and_repeat(self):
        boy = Boy()
        boy.handle_events([('left', True), ('right', True)])
        self.assertEqual(boy.state, 'IDLE')
        boy.handle_events([('left', False)])
        boy.update(.3)
        boy.handle_events([('right', True)] * 20)
        boy.update(.7)
        self.assertAlmostEqual(boy.x, 500)
        boy.clear_inputs()
        self.assertEqual((boy.state, boy.speed), ('IDLE', 0))

    def test_idle_and_sleep_threshold_and_animation(self):
        boy = Boy()
        boy.update(4.999)
        self.assertEqual(boy.state, 'IDLE')
        boy.update(.001)
        self.assertEqual((boy.state, boy.frame), ('SLEEP', 0))
        boy.update(.499)
        self.assertEqual(boy.frame, 0)
        boy.update(.001)
        self.assertEqual(boy.frame, 1)

    def test_auto_speed_curve_and_no_early_exit(self):
        boy = Boy()
        boy.handle_events([('d', True)])
        for delta, speed in [(1, 200), (2, 400), (.5, 300), (1.499, .2)]:
            boy.update(delta)
            self.assertEqual(boy.state, 'AUTO_RUN')
            self.assertAlmostEqual(boy.speed, speed)
        boy.update(.001)
        self.assertEqual((boy.state, boy.speed, boy.scale), ('IDLE', 0, 1))

    def test_auto_ignores_arrows_and_extra_auto_keys(self):
        boy = Boy()
        boy.handle_events([('d', True)])
        boy.update(.25)
        snapshot = (boy.direction, boy.speed, boy.auto_elapsed, boy.frame_time)
        boy.handle_events([('left', True), ('a', True), ('d', True), ('right', True)])
        boy.handle_events([('right', False), ('d', False)])
        self.assertEqual((boy.direction, boy.speed, boy.auto_elapsed, boy.frame_time), snapshot)

    def test_boundaries_keep_inward_direction_and_idle_facing(self):
        for x, key, direction, expected in [(50, 'd', 1, 100), (750, 'a', -1, 700),
                                             (50, 'a', 1, 100), (750, 'd', -1, 700)]:
            boy = Boy()
            boy.x = x
            boy.direction = -direction
            boy.update(0)
            self.assertEqual(boy.direction, -direction)
            boy.handle_events([(key, True)])
            self.assertEqual((boy.x, boy.direction), (expected, direction))

    def test_braking_reflection_keeps_time_and_speed(self):
        boy = Boy()
        boy.handle_events([('a', True)])
        boy.auto_elapsed = 3.5
        boy.braking = True
        boy.speed = 300
        boy.x = 100
        boy.update(.01)
        self.assertTrue(boy.braking)
        self.assertEqual(boy.direction, 1)
        self.assertAlmostEqual(boy.speed, 298)
        self.assertAlmostEqual(boy.auto_elapsed, 3.51)

    def test_frame_partition_does_not_change_auto_distance_or_idle_time(self):
        for key, expected_x in [('a', 450), ('d', 350)]:
            for dt in [1 / 30, 1 / 60, 1 / 144, .017, .3, 1.1, 6.0]:
                boy = Boy()
                boy.handle_events([(key, True)])
                remaining = 6.0
                while remaining > 1e-10:
                    step = min(dt, remaining)
                    boy.update(step)
                    remaining -= step
                self.assertEqual(boy.state, 'IDLE', (key, dt))
                self.assertAlmostEqual(boy.x, expected_x, places=7)
                self.assertAlmostEqual(boy.idle_elapsed, 1, places=7)

    def test_large_frame_accounts_for_auto_idle_and_sleep(self):
        boy = Boy()
        boy.handle_events([('d', True)])
        boy.update(11.25)
        self.assertEqual((boy.state, boy.speed, boy.scale), ('SLEEP', 0, 1))
        self.assertEqual(boy.frame, 2)
        self.assertAlmostEqual(boy.frame_time, .25)
        self.assertAlmostEqual(boy.x, 350)

    def test_invalid_delta_is_rejected(self):
        for delta in [-.1, float('inf'), float('nan')]:
            with self.assertRaises(ValueError):
                Boy().update(delta)

    def test_uml_connections_match_machine(self):
        source = (Path(__file__).resolve().parents[1] / 'state_diagram.puml').read_text(encoding='utf-8')
        shown = set(re.findall(r'^(\w+) --> (\w+)', source, re.M))
        boy = Boy()
        actual = {(state, transition.dest) for event in boy.machine.events.values()
                  for state, transitions in event.transitions.items() for transition in transitions}
        self.assertEqual(shown, actual)

    def test_repeated_cycles_restore_state_and_pose(self):
        boy = Boy()
        for cycle in range(40):
            boy.update(5)
            self.assertEqual(boy.state, 'SLEEP')
            key = 'left' if cycle % 2 else 'right'
            boy.handle_events([(key, True)])
            self.assertEqual(boy.state, 'WALK')
            self.assertEqual((boy.frame, boy.frame_time), (0, 0))
            boy.update(.2)
            boy.handle_events([(key, False)])
            self.assertEqual(boy.idle_elapsed, 0)
            auto = 'a' if cycle % 2 else 'd'
            boy.handle_events([(auto, True)])
            self.assertEqual(boy.scale, 2)
            boy.update(5)
            self.assertEqual((boy.state, boy.speed, boy.scale), ('IDLE', 0, 1))
            self.assertEqual((boy.idle_elapsed, boy.frame, boy.frame_time), (0, 0, 0))
            boy.handle_events([(auto, False)])
            self.assertTrue(50 <= boy.x <= 750)

    def test_held_arrow_needs_release_after_auto(self):
        boy = Boy()
        boy.handle_events([('d', True), ('left', True)])
        boy.update(5)
        boy.handle_events([('d', False), ('left', True)])
        self.assertEqual(boy.state, 'IDLE')
        boy.update(.2)
        boy.handle_events([('left', False), ('left', True)])
        self.assertEqual((boy.state, boy.direction), ('WALK', -1))

    def test_state_changes_start_animation_at_zero(self):
        boy = Boy()
        boy.update(.124)
        boy.handle_events([('left', True)])
        boy.update(.124)
        self.assertEqual(boy.frame, 0)
        boy.handle_events([('left', False)])
        boy.update(5)
        boy.update(.499)
        self.assertEqual(boy.frame, 0)
        boy.handle_events([('d', True)])
        self.assertEqual((boy.frame, boy.frame_time), (0, 0))


if __name__ == '__main__':
    unittest.main()
