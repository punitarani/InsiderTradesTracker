"""
Test Configs
"""

import unittest

import config


class TestConfig(unittest.TestCase):
    """
    Test Config.py
    """

    def test_config(self):
        """
        Test Config
        """

        # Check if config.yaml exists
        self.assertTrue(config.PROJECT_PATH.joinpath('config.yaml').exists())

        # Check if Deployment exists and is not empty
        self.assertTrue(isinstance(config.DEPLOYMENT, str))
        self.assertTrue(config.DEPLOYMENT == "D" or config.DEPLOYMENT == 'P')

        # Check if Name exists and is not empty
        self.assertTrue(isinstance(config.NAME, str))
        self.assertTrue(len(config.NAME.strip()) > 0)

        # Check if email exists and is appropriate
        self.assertTrue(isinstance(config.EMAIL, str))
        self.assertIn('@', config.EMAIL)
        self.assertIn('.', config.EMAIL)


if __name__ == '__main__':
    unittest.main()
