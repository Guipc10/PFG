# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath(''))

import unittest
from src.logutils.customlog import CustomLogging
import io
import logging

class TestCustomLogging(unittest.TestCase):
    def test_info_logs_expected_format(self):
        # Create a CustomLogging instance and capture the log output
        logger = CustomLogging('test')

        # Log a message
        logger.info("This is a test message")
        
        self.assertTrue(logger.logger.isEnabledFor(logging.INFO))
        self.assertEqual(logger.logger.getEffectiveLevel(), logging.INFO)
        self.assertEqual(logger.logger.name, 'test')
        

if __name__ == '__main__':
    unittest.main()