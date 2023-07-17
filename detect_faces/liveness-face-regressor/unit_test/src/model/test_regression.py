# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath(''))

import unittest
from unittest.mock import call
import numpy as np
from unittest.mock import MagicMock, patch, Mock
from src.model.regression import RegressorResponse
from src.model.regression import Regressor
from shapely.geometry import Polygon

class TestRegressorResponse(unittest.TestCase):
    def test_standardize(self):
        regressor_response = RegressorResponse()

        bboxes_lst = [[1, 2, 3, 4], [5, 6, 7, 8]]
        keypoints_68_lst = [(1, 2), (3, 4)]
        keypoints_478_lst = [(5, 6), (7, 8)]
        yaw_lst = [1.0, 2.0]
        pitch_lst = [3.0, 4.0]
        scores_lst = [0.5, 0.6]
        has_obstruction_lst = [True, False]
        correctly_framed = [True, False]

        regressor_response.standardize(
            bboxes_lst, keypoints_68_lst, keypoints_478_lst, yaw_lst, pitch_lst, scores_lst, has_obstruction_lst, correctly_framed
        )

        self.assertEqual(regressor_response.keypoints, keypoints_68_lst)
        self.assertEqual(regressor_response.keypoints_478, keypoints_478_lst)
        self.assertEqual(regressor_response.yaw_lst, yaw_lst)
        self.assertEqual(regressor_response.pitch_lst, pitch_lst)
        self.assertEqual(regressor_response.bboxes, bboxes_lst)
        self.assertEqual(regressor_response.scores, scores_lst)
        self.assertEqual(regressor_response.has_obstruction, has_obstruction_lst)
        self.assertEqual(regressor_response.correctly_framed, correctly_framed)

    def test_standardize_with_empty_inputs(self):
        regressor_response = RegressorResponse()

        bboxes_lst = []
        keypoints_68_lst = []
        keypoints_478_lst = []
        yaw_lst = []
        pitch_lst = []
        scores_lst = []
        has_obstruction_lst = []
        correctly_framed = []

        regressor_response.standardize(
            bboxes_lst, keypoints_68_lst, keypoints_478_lst, yaw_lst, pitch_lst, scores_lst, has_obstruction_lst, correctly_framed
        )

        self.assertEqual(regressor_response.keypoints, keypoints_68_lst)
        self.assertEqual(regressor_response.keypoints_478, keypoints_478_lst)
        self.assertEqual(regressor_response.yaw_lst, yaw_lst)
        self.assertEqual(regressor_response.pitch_lst, pitch_lst)
        self.assertEqual(regressor_response.bboxes, bboxes_lst)
        self.assertEqual(regressor_response.scores, scores_lst)
        self.assertEqual(regressor_response.has_obstruction, has_obstruction_lst)
        self.assertEqual(regressor_response.correctly_framed, correctly_framed)

class TestRegressor(unittest.TestCase):
    def setUp(self):
        self.args = {}
        self.regressor = Regressor(self.args)
        self.regressor.face_mesh = MagicMock()
        self.regressor.palm_detector = MagicMock()
        self.regressor.face_mesh.detect = Mock()
        self.regressor.palm_detector.detect = Mock()
        self.decode_img = patch('src.model.util.utils.Utils.decode_img', new=MagicMock())
        self.standard = patch('src.model.regression.RegressorResponse', new=MagicMock())
        self.expected_output = {
            'bboxes': [(5, 10, 8, 3), (5, 10, 8, 3)],
            'kps_68': [[(5, 10), (5, 10)], [(5, 10), (5, 10)]],
            'kps_478': [[(5, 10), (5, 10)], [(5, 10), (5, 10)]],
            'yaw_lst': [0.5, 0.5],
            'pitch_lst': [0.66, 0.66],
            'conf_scores': [0.5, 0.5],
            'has_obstruction': [True, True],
            'correctly_framed': [True, True]
        }
        self.standardize = patch('src.model.regression.RegressorResponse.standardize', new=MagicMock(return_value = self.expected_output))
        self.convert_coordinate_format = patch('src.model.regression.Utils.convert_coordinate_format', new=MagicMock())
        self.polygon_intersects = patch('src.model.regression.Polygon.intersects', new=MagicMock())

        self.palm = MagicMock()
        self.palm.get_polygon = MagicMock()
        self.palm.get_polygon.return_value = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])

        self.polygon = Mock()
        self.polygon.intersects.side_effect = [True, True]
        
        self.decode_img.start()
        self.standard.start()
        self.standardize.start()

        self.convert_coordinate_format.start()
        self.polygon.start()

        self.addCleanup(self.decode_img.stop)
        self.addCleanup(self.standard.stop)
        self.addCleanup(self.standardize.stop)
        self.addCleanup(self.convert_coordinate_format.stop)
        self.addCleanup(self.polygon.stop)
        
    def test_detect(self):
        # Test input: list of image bytes
        image_bytes = [
            b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAAAAACoBHk5AAAAGElEQVQIHRXBgQ0AAABAIP5/2pRMJpPJAgB4AAZhpcJSAAAAAElFTkSuQmCC', 
            b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAAAAACoBHk5AAAAGElEQVQIHRXBgQ0AAABAIP5/2pRMJpPJAgB4AAZhpcJSAAAAAElFTkSuQmCC'
        ]

        # Set the expected output for the mocked functions
        detections = [
            {
                'conf_score': 0.5,
                'bbox': (5, 10, 8, 3),
                'correctly_framed': True,
                'keypoints_68': [(5, 10), (5, 10)],
                'keypoints_478': [(5, 10), (5, 10)],
                'yaw': 0.5,
                'pitch': 0.66
            },
            {
                'conf_score': 0.8,
                'bbox': (5, 10, 8, 3),
                'correctly_framed': True,
                'keypoints_68': [(5, 10), (5, 10)],
                'keypoints_478': [(5, 10), (5, 10)],
                'yaw': 0.45,
                'pitch': 0.10
            }
        ]

        self.regressor._check_obstruction = Mock()
        self.regressor.face_mesh.detect.side_effect = detections
        self.regressor.palm_detector.detect.side_effect = [True, False]
        self.regressor._check_obstruction.return_value = True
        self.standard.return_value = None
        self.decode_img.side_effect = [np.zeros((5, 5), dtype=np.uint8)]

        self.maxDiff = None
        # Call the function and assert the output
        actual_output = self.regressor.detect(image_bytes)
        self.assertEqual(
            call.standardize(((5, 10, 8, 3), (5, 10, 8, 3)), ([(5, 10), (5, 10)], [(5, 10), (5, 10)]), ([(5, 10), (5, 10)], [(5, 10), (5, 10)]), (0.5, 0.45), (0.66, 0.1), (0.5, 0.8), True, (True, True)), 
            actual_output["method_calls"][0])
        self.regressor.palm_detector.detect.assert_called()
        self.regressor._check_obstruction.assert_called()

    def test_check_obstruction(self):
        # Test input: list of palm detection results and list of bounding boxes
        palms_lst = [[self.palm], [self.palm]]
        bboxes = [[[ 0, 1, 2, 3]], [[4, 5, 6, 7]]]

        # Set the expected output for the mocked functions
        self.convert_coordinate_format.side_effect = [(0, 0), (0, 2), (2, 2), (2, 0)]

        self.assertEqual(self.regressor._check_obstruction(palms_lst, bboxes), [False, False])

if __name__ == '__main__':
    unittest.main()