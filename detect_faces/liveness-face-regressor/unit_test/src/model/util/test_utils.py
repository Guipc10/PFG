# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath(''))

import unittest
import numpy as np
from src.model.util.utils import Utils 

class TestUtils(unittest.TestCase):
    def test_convert_coordinate_format(self):
        bbox = [1, 2, 3, 4]
        expected_output = [(1, 4), (3, 4), (3, 2), (1, 2)]
        self.assertEqual(Utils.convert_coordinate_format(bbox), expected_output)

        bbox = [5, 6, 7, 8]
        expected_output = [(5, 8), (7, 8), (7, 6), (5, 6)]
        self.assertEqual(Utils.convert_coordinate_format(bbox), expected_output)

        bbox = [-1, -2, -3, -4]
        expected_output = [(-1, -4), (-3, -4), (-3, -2), (-1, -2)]
        self.assertEqual(Utils.convert_coordinate_format(bbox), expected_output)

    def test_distance_yaw(self):
        point_a = np.array([3, 4])
        point_b = np.array([1, 2])
        self.assertEqual(Utils.distance_yaw(point_a, point_b), 0)

        point_a = np.array([1, 2])
        point_b = np.array([3, 4])
        self.assertAlmostEqual(Utils.distance_yaw(point_a, point_b), 2.8284271247461903)

    def test_euclidean_distance(self):
        point_a = np.array([3, 4])
        point_b = np.array([1, 2])
        self.assertAlmostEqual(Utils.euclidean_distance(point_a, point_b), 2.8284271247461903)

        point_a = np.array([1, 2])
        point_b = np.array([3, 4])
        self.assertAlmostEqual(Utils.euclidean_distance(point_a, point_b), 2.8284271247461903)

    def test_crop_img(self):
        # Test with valid input and no cropping needed
        img = np.zeros((5, 5), dtype=np.uint8)
        roi_box = [1, 1, 3, 3]
        expected_output = np.zeros((2, 2), dtype=np.uint8)
        self.assertEqual(Utils.crop_img(img, roi_box).tolist(), expected_output.tolist())
        
        # Test with valid input and cropping needed
        img = np.zeros((5, 5), dtype=np.uint8)
        roi_box = [-1, -1, 7, 7]
        expected_output = np.zeros((8, 8), dtype=np.uint8)
        self.assertEqual(Utils.crop_img(img, roi_box).tolist(), expected_output.tolist())
        
    def test_encode_img_b(self):
        # Test with valid input
        img = np.zeros((5, 5), dtype=np.uint8)
        expected_output = b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAAAAACoBHk5AAAAGElEQVQIHRXBgQ0AAABAIP5/2pRMJpPJAgB4AAZhpcJSAAAAAElFTkSuQmCC'
        self.assertEqual(Utils.encode_img_b(img), expected_output)
        
    # def test_decode_img(self):
    #     # Test with valid input
    #     import cv2
    #     img = np.zeros((5, 5), dtype=np.uint8)
    #     _, buf = cv2.imencode(".png", img)

    #     expected_output = np.zeros((5, 5), dtype=np.uint8)
    #     self.assertEqual(Utils.decode_img(buf.tobytes()).tolist(), expected_output.tolist())


if __name__ == '__main__':
    unittest.main()