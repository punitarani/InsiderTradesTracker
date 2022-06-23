"""
Test Logging
"""

import logging
import unittest
from datetime import datetime, timedelta
from time import time

from common import Logger


class LoggerTests(unittest.TestCase):
    """
    Test Logger
    """

    def test_init(self):
        """
        Test Class Initialization
        """

        test_logger = Logger('test')
        self.assertEqual(test_logger.name, 'test')
        self.assertEqual(test_logger.add_file_handler, True)
        self.assertEqual(test_logger.add_stream_handler, True)
        self.assertEqual(test_logger.level, logging.DEBUG)
        self.assertEqual(test_logger.root_name, 'test')
        self.assertEqual(test_logger.filename.name, 'test.log')

        logger = test_logger.get_logger()
        self.assertIsInstance(logger, logging.Logger)

    def test_init_log(self):
        """
        Test get_logger() and initialization of logging.logger objects
        """

        now = time()
        logger_name = 'test'
        test_logger = Logger(logger_name)
        test_logger.get_logger()

        log_messages = [
            f"Getting logger: {logger_name}",
            f"Getting logger: {logger_name}",
            f"Getting logger: {logger_name}",
            f"Caching logger: {logger_name}",
            f"Creating logger: {logger_name}",
        ]

        # Read the last 3 lines of the log file
        with open(test_logger.filename, 'r') as f:
            lines = f.readlines()[-3:]

            # Check the log messages
            for line in lines:
                log_split = [x.strip() for x in line.split(' - ')]

                log_time = datetime.strptime(log_split[0].strip(), '%Y-%m-%d %H:%M:%S,%f')
                self.assertAlmostEqual(log_time.timestamp(), now,
                                       delta=timedelta(seconds=1).total_seconds())
                self.assertEqual(log_split[1], logger_name)
                self.assertEqual(log_split[2], 'INFO')
                self.assertEqual(log_split[3], log_messages.pop(0))

    def test_log(self):
        """
        Test logging
        """

        now = time()
        test_logger = Logger('test')
        logger = test_logger.get_logger()

        logger.debug('Test DEBUG')
        logger.info('Test INFO')
        logger.warning('Test WARNING')
        logger.error('Test ERROR')
        logger.critical('Test CRITICAL')

        log_messages = [
            'Test DEBUG',
            'Test INFO',
            'Test WARNING',
            'Test ERROR',
            'Test CRITICAL'
        ]

        # Read the last 5 lines of the log file
        with open(test_logger.filename, 'r') as f:
            lines = f.readlines()[-5:]

            # Check the log messages
            for i, line in enumerate(lines):
                log_split = [x.strip() for x in line.split(' - ')]

                log_time = datetime.strptime(log_split[0].strip(), '%Y-%m-%d %H:%M:%S,%f')
                self.assertAlmostEqual(log_time.timestamp(), now,
                                       delta=timedelta(seconds=1).total_seconds())
                self.assertEqual(log_split[1], 'test')
                self.assertEqual(log_split[2], log_messages[i].split(' ')[-1].strip())
                self.assertEqual(log_split[3], log_messages[i])

    def test_log_child(self):
        """
        Test logging of child loggers
        """

        now = time()
        test_logger = Logger('test.subtest')
        logger = test_logger.get_logger()
        self.assertEqual(test_logger.name, 'test.subtest')
        self.assertEqual(test_logger.root_name, 'test')
        self.assertEqual(test_logger.filename.name, 'test.log')

        logger.debug('Subtest DEBUG')
        logger.info('Subtest INFO')
        logger.warning('Subtest WARNING')
        logger.error('Subtest ERROR')
        logger.critical('Subtest CRITICAL')

        log_messages = [
            'Subtest DEBUG',
            'Subtest INFO',
            'Subtest WARNING',
            'Subtest ERROR',
            'Subtest CRITICAL'
        ]

        # Read the last 5 lines of the log file
        with open(test_logger.filename, 'r') as f:
            lines = f.readlines()[-5:]

            # Check the log messages
            for i, line in enumerate(lines):
                log_split = [x.strip() for x in line.split(' - ')]

                log_time = datetime.strptime(log_split[0].strip(), '%Y-%m-%d %H:%M:%S,%f')
                self.assertAlmostEqual(log_time.timestamp(), now,
                                       delta=timedelta(seconds=1).total_seconds())
                self.assertEqual(log_split[1], 'test.subtest')
                self.assertEqual(log_split[2], log_messages[i].split(' ')[-1])
                self.assertEqual(log_split[3], log_messages[i])


if __name__ == '__main__':
    unittest.main()
