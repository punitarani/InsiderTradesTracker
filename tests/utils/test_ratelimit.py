"""
Test RateLimit
"""

import unittest
from time import time, sleep

from tracker.utils import RateLimit, RateLimitException


class RateLimitTests(unittest.TestCase):
    """
    Test RateLimit
    """

    def test_basic(self):
        """
        Test basic ratelimiting (1)
        """

        @RateLimit(limit=10, period=1, max_wait=None)
        def test_func(a: int) -> int:
            sleep(0.1)
            return a

        start_time = time()
        for i in range(10):
            self.assertEqual(test_func(i), i)
        end_time = time()

        # ~0.1s for first 10 calls => ~1s total
        self.assertAlmostEqual(end_time - start_time, 1, delta=0.15)

    def test_basic_2(self):
        """
        Test basic ratelimiting (2)
        """

        @RateLimit(limit=10, period=1, max_wait=None)
        def test_func(a: int) -> int:
            sleep(0.05)
            return a

        start_time = time()
        for i in range(20):
            self.assertEqual(test_func(i), i)
        end_time = time()

        # ~0.05s for first 10 calls before rate limit is reached => ~0.5s total
        # ~0.5s wait before next 10 calls at ~0.05s each => ~1s total
        self.assertAlmostEqual(end_time - start_time, 1.5, delta=0.2)

    def test_basic_3(self):
        """
        Test basic ratelimiting (3)
        """

        @RateLimit(limit=10, period=5, max_wait=None)
        def test_func(a: int) -> int:
            sleep(0.1)
            return a

        start_time = time()
        for i in range(30):
            self.assertEqual(test_func(i), i)
        end_time = time()

        # ~0.1s for first 10 calls before rate limit is reached => ~1s execution time
        # 5-1s wait => ~4s wait time = ~5s total
        # ~0.1s for next 10 calls => ~1s execution time => ~6s total
        # Repeat once more for a total time of ~12s
        self.assertAlmostEqual(end_time - start_time, 13, delta=2.5)

    def test_max_wait(self):
        """
        Test max_wait param
        """

        @RateLimit(limit=4, period=2, max_wait=4)
        def test_func(a: int) -> int:
            sleep(0.05)
            return a

        start_time = time()
        for i in range(20):
            try:
                self.assertEqual(test_func(i), i)
            except RateLimitException:
                self.assertAlmostEqual(i, 14, delta=2)
                break
        end_time = time()

        self.assertAlmostEqual(7.5, end_time - start_time, delta=1)


if __name__ == '__main__':
    unittest.main()
