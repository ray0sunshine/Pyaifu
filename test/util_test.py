import helper.util as util
import unittest

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

TRIALS = 3000
TRIALS_SHORT = 10


class util_test(unittest.TestCase):
    def test_lerp(self):
        self.assertEqual(util.lerp((0, 0), (1, 1)), (0.5, 0.5))
        self.assertEqual(util.lerp((0, 0), (1, 1), 0), (0, 0))
        self.assertEqual(util.lerp((0, 0), (1, 2), 0.9), (0.9, 1.8))
        self.assertEqual(util.lerp((-1, -3), (1, 3), 0.2), (-0.6, -1.8))

    def test_ilerp(self):
        self.assertEqual(util.ilerp((0, 0), (2, 2)), (1, 1))
        self.assertEqual(util.ilerp((0, 0), (1, 1), 0.6), (1, 1))
        self.assertEqual(util.ilerp((0, 0), (1, 1), 0.4), (0, 0))

    def test_normal1(self):
        res = [util.normalRange(3, 7) for _ in range(TRIALS)]
        self.assertAlmostEqual(sum(res) / len(res), 5, places=1)
        self.assertGreaterEqual(7, max(res))
        self.assertLessEqual(3, min(res))

    def test_normal2(self):
        res = [util.normalRange2(5, 3) for _ in range(TRIALS)]
        self.assertAlmostEqual(sum(res) / len(res), 5, places=1)
        self.assertGreaterEqual(8, max(res))
        self.assertLessEqual(2, min(res))

    def test_point1(self):
        for _ in range(TRIALS):
            res = util.rpoint((0, 100), (100, 200))
            self.assertTrue(0 <= res[0] <= 100)
            self.assertTrue(100 <= res[1] <= 200)

            res = util.rpoint((100, 200), (0, 100))
            self.assertTrue(0 <= res[0] <= 100)
            self.assertTrue(100 <= res[1] <= 200)

            res = util.rpoint((0, 200), (100, 100))
            self.assertTrue(0 <= res[0] <= 100)
            self.assertTrue(100 <= res[1] <= 200)

            res = util.rpoint((100, 100), (0, 200))
            self.assertTrue(0 <= res[0] <= 100)
            self.assertTrue(100 <= res[1] <= 200)

    def test_point2(self):
        for _ in range(TRIALS):
            res = util.cpoint((0, 0), (6, 8))
            self.assertLessEqual(util.dist(res, (3, 4)), 5)

    def test_wait(self):
        print(sum([util.wait(0) for _ in range(TRIALS_SHORT)]) / TRIALS_SHORT)
