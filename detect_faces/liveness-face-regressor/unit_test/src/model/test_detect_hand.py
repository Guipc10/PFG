# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath(''))

import unittest
import mediapipe as mp
import numpy as np
import cv2
from src.model.detect_hand import Palm, PalmDetector
from shapely.geometry import Polygon

class TestPalm(unittest.TestCase):

    def test_init(self):
        # Test with an empty list of keypoints
        palm = Palm()
        self.assertEqual(palm._kps, [])
        self.assertIsNone(palm._poly)

        # Test with a list of keypoints
        kps = [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [0.0, 0.0]]
        palm = Palm(kps)
        self.assertEqual(palm._kps, kps)
        
        # self.assertIsInstance(palm._poly, Polygon)
        self.assertEqual(
                [list(x) for x in palm._poly.exterior.coords.xy], 
                [[x for x, y in kps], [y for x, y in kps]])

    def test_get_polygon(self):
        # Test with a Palm object initialized with keypoints
        kps = [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [0.0, 0.0]]
        palm = Palm(kps)
        polygon = palm.get_polygon()
        self.assertIsInstance(polygon, Polygon)

        self.assertEqual(
                [list(x) for x in polygon.exterior.coords], kps)

        # Test with a Palm object initialized with an empty list of keypoints
        palm = Palm()
        polygon = palm.get_polygon()
        self.assertIsNone(polygon)

    def test_get_kps(self):
        # Test with a Palm object initialized with keypoints
        kps = [[0, 0], [1, 1], [2, 2]]
        palm = Palm(kps)
        self.assertEqual(palm.get_kps(), kps)

        # Test with a Palm object initialized with an empty list of keypoints
        palm = Palm()
        self.assertEqual(palm.get_kps(), [])


class TestPalmDetector(unittest.TestCase):
    def setUp(self):
        self.max_num_hands = 2
        self.min_detection_confidence = 0.5
        self.min_tracking_confidence = 0.5
        self.palm_detector = PalmDetector(
            max_num_hands=self.max_num_hands, 
            min_detection_confidence=self.min_detection_confidence, 
            min_tracking_confidence=self.min_tracking_confidence)

    def test_init(self):
        self.assertIsInstance(self.palm_detector.detector, mp.solutions.hands.Hands)
        self.assertEqual(self.palm_detector.PALM_IDXS, [0, 4, 8, 12, 16, 20])

    def test_detect(self):
        # Test with an image that contains no hands
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        palm_detector = PalmDetector()
        palms = palm_detector.detect(img)
        self.assertEqual(palms, [])

        # Test with an image that contains a single hand
        # Open image with a single hand
        img = cv2.imread('unit_test/src/hand.jpg')
        palm_detector = PalmDetector()
        palms = palm_detector.detect(img)
        self.assertEqual(len(palms), 1)