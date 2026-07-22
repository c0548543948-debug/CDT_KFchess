import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from rendering.interpolator import interpolate_position, interpolate_jump_fraction


class TestInterpolatePosition(unittest.TestCase):

    def test_before_start(self):
        row, col = interpolate_position(0, 0, 8, 8, start_time_ms=1000, duration_ms=1000, current_time_ms=500)
        self.assertEqual(row, 0)
        self.assertEqual(col, 0)

    def test_after_end(self):
        row, col = interpolate_position(0, 0, 8, 8, start_time_ms=1000, duration_ms=1000, current_time_ms=3000)
        self.assertEqual(row, 8)
        self.assertEqual(col, 8)

    def test_halfway(self):
        row, col = interpolate_position(0, 0, 8, 8, start_time_ms=0, duration_ms=1000, current_time_ms=500)
        self.assertEqual(row, 4.0)
        self.assertEqual(col, 4.0)

    def test_zero_duration(self):
        row, col = interpolate_position(0, 0, 8, 8, start_time_ms=0, duration_ms=0, current_time_ms=500)
        self.assertEqual(row, 8)
        self.assertEqual(col, 8)


class TestInterpolateJumpFraction(unittest.TestCase):

    def test_before_start(self):
        self.assertEqual(interpolate_jump_fraction(start_time_ms=1000, duration_ms=500, current_time_ms=500), 0.0)

    def test_after_end(self):
        self.assertEqual(interpolate_jump_fraction(start_time_ms=1000, duration_ms=500, current_time_ms=2000), 1.0)

    def test_halfway(self):
        self.assertEqual(interpolate_jump_fraction(start_time_ms=0, duration_ms=1000, current_time_ms=500), 0.5)

    def test_zero_duration(self):
        self.assertEqual(interpolate_jump_fraction(start_time_ms=0, duration_ms=0, current_time_ms=500), 1.0)


if __name__ == "__main__":
    unittest.main()