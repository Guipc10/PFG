# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath(''))

import unittest
from unittest.mock import MagicMock, patch
from src.logutils.filter import AppFilter

class TestAppFilter(unittest.TestCase):
    @patch('src.logutils.filter.get_request_id')
    def test_filter_sets_request_id(self, get_request_id):
        # Set up test data
        record = MagicMock()
        
        # Mock the get_request_id function with multiple return values
        get_request_id.side_effect = ['12345', 'abcde', "", None, 13215]

        # Create an instance of the class to test
        app_filter = AppFilter()
        
        # Call the method we want to test and assert that the request_id attribute on 
        # the record is set as expected
        result1 = app_filter.filter(record)
        self.assertEqual(record.request_id, '12345')
        result2 = app_filter.filter(record)
        self.assertEqual(record.request_id, 'abcde')
        result3 = app_filter.filter(record)
        self.assertEqual(record.request_id, "")
        result4 = app_filter.filter(record)
        self.assertEqual(record.request_id, None)
        result5 = app_filter.filter(record)
        self.assertEqual(record.request_id, 13215)

        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        self.assertTrue(result4)
        self.assertTrue(result5)


if __name__ == '__main__':
    unittest.main()