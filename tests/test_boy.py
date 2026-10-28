"""Behaviour checks without opening a graphics window."""
import unittest

from boy import Boy


class PlayerTests(unittest.TestCase):
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
