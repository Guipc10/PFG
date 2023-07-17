# This is a unit test to the face_mesh.py file.
import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from src.model.face_mesh import FaceMeshDetection, FaceMesh
from src.model.util.utils import Utils
from src.model.util.arguments import ServerArgs


class TestFaceMeshDetection(unittest.TestCase):
    def setUp(self):
        self.keypoints_478 = np.ones((478, 3))
        self.keypoints_68 = np.ones((68, 3))
        self.args = ServerArgs()

    def test_init(self):
        # Create an instance of the class
        face_mesh = FaceMeshDetection()
        self.assertIsNone(face_mesh.keypoints_68)
        self.assertIsNone(face_mesh.keypoints_478)
        self.assertIsNone(face_mesh.yaw)
        self.assertIsNone(face_mesh.pitch)
        self.assertIsNone(face_mesh.bbox)
        self.assertIsNone(face_mesh.correctly_framed)
        self.assertIsNone(face_mesh.conf_score)

    def test_expand_bbox(self):
        # Create an instance of the class
        face_mesh = FaceMeshDetection()

        # Test with a bbox
        bbox = [100, 150, 200, 250]
        new_bbox = face_mesh._expand_bbox(bbox)
        self.assertEqual(new_bbox, [75, 125, 225, 275])

        # Test with a None bbox
        bbox = None
        new_bbox = face_mesh._expand_bbox(bbox)
        self.assertIsNone(new_bbox)

    def test_process_kps(self):
        # Create an instance of the class
        face_mesh = FaceMeshDetection()

        # Create a test case where keypoints are present
        mp_result = MagicMock()
        mp_result.multi_face_landmarks = [MagicMock()]
        mp_result.multi_face_landmarks[0].landmark = [MagicMock() for i in range(478)]
        for i in range(478):
            mp_result.multi_face_landmarks[0].landmark[i].x = i
            mp_result.multi_face_landmarks[0].landmark[i].y = i
            mp_result.multi_face_landmarks[0].landmark[i].z = i
        img_height = 480
        img_width = 640
        keypoints_478, keypoints_68, bbox = face_mesh._process_kps(mp_result, img_height, img_width)
        self.assertEqual(keypoints_478.shape, (478, 3))
        self.assertEqual(keypoints_68.shape, (68, 3))
        self.assertEqual(bbox, [0, 0, 305280, 228960])

        # Create a test case where keypoints are not present
        mp_result.multi_face_landmarks = None
        keypoints_478, keypoints_68, bbox = face_mesh._process_kps(mp_result, img_height, img_width)
        self.assertIsNone(keypoints_478)
        self.assertIsNone(keypoints_68)
        self.assertIsNone(bbox)

    @patch.object(FaceMeshDetection, "LEFT_EYE_IDXS", [0, 1 ,2])
    @patch.object(FaceMeshDetection, "RIGHT_EYE_IDXS", [0, 1 ,2])
    @patch.object(FaceMeshDetection, "NOSE_IDXS", [0, 1 ,2])
    @patch.object(FaceMeshDetection, "MOUTH_IDXS", [0, 1 ,2])
    def test__check_framing(self):
        # Create an instance of the class
        face_mesh = FaceMeshDetection()

        # test with keypoints that are within limits
        keypoints_68 = np.array([[0, 0], [100, 100], [50, 50]])
        img_width = 200
        img_height = 200
        correctly_framed = face_mesh._check_framing(keypoints_68, img_width, img_height)
        self.assertTrue(correctly_framed)

        # test with keypoints that are outside the limits
        keypoints_68 = np.array([[-1, 0], [201, 201], [50, 50]])
        correctly_framed = face_mesh._check_framing(keypoints_68, img_width, img_height)
        self.assertFalse(correctly_framed)

        # test with None keypoints
        keypoints_68 = None
        correctly_framed = face_mesh._check_framing(keypoints_68, img_width, img_height)
        self.assertIsNone(correctly_framed)

    @patch.object(Utils, 'distance_yaw')
    def test_get_yaw_valid_input(self, mock_distance_yaw):
        # Test case when line A and line B are equal
        mock_distance_yaw.side_effect = [10, 10]
        yaw = FaceMeshDetection._get_yaw(self, self.keypoints_68)
        self.assertEqual(yaw, 0)

        # Test case when line A < line B
        mock_distance_yaw.side_effect = [10, 20]
        yaw = FaceMeshDetection._get_yaw(self, self.keypoints_68)
        expected_yaw = np.arcsin(1 - (10 / 20))
        self.assertEqual(yaw, expected_yaw)

        # Test case when line A > line B
        mock_distance_yaw.side_effect = [20, 10]
        yaw = FaceMeshDetection._get_yaw(self, self.keypoints_68)
        expected_yaw = -np.arcsin(1 - (10 / 20))
        self.assertEqual(yaw, expected_yaw)

    def test_get_yaw_invalid_input(self):
        # Test case with None input
        yaw = FaceMeshDetection._get_yaw(self, None)
        self.assertIsNone(yaw)
    
    @patch.object(Utils, 'euclidean_distance')
    @patch.object(np, 'arcsin')
    def test_get_pitch_valid_input(self, mock_euclidean_distance, mock_arcsin):
        mock_euclidean_distance.side_effect = [10, 20]
        pitch = FaceMeshDetection._get_pitch(self, self.keypoints_68)        
        
        mock_arcsin.side_effect = [0.5, 0.666]

        self.assertEqual(pitch, 15.0)

    def test_get_pitch_invalid_input(self):
        # Test case with None input
        pitch = FaceMeshDetection._get_pitch(self, None)
        self.assertIsNone(pitch)
    
    def test_process_face_detection_valid_input(self):
        mp_result = MagicMock()
        mp_result.face_detections = [MagicMock(score=[0.8])]
        conf_score = FaceMeshDetection._process_face_detection(self, mp_result)
        self.assertEqual(conf_score, 0.8)

    def test_process_face_detection_invalid_input(self):
        # Test case with no face detections
        mp_result = MagicMock()
        mp_result.face_detections = []
        conf_score = FaceMeshDetection._process_face_detection(self, mp_result)
        self.assertEqual(conf_score, 0.0)

    def test_standardize_valid_input(self):
        fmd = FaceMeshDetection()

        fmd._process_kps = MagicMock()
        fmd._process_kps.return_value = self.keypoints_478, self.keypoints_68, [[0, 0, 100, 100]]
        fmd._check_framing = MagicMock()
        fmd._check_framing.return_value = True
        fmd._expand_bbox = MagicMock()
        fmd._expand_bbox.return_value = (0, 1, 2, 3)
        fmd._get_yaw = MagicMock()
        fmd._get_yaw.return_value = 0.5
        fmd._get_pitch = MagicMock()
        fmd._get_pitch.return_value = 0.666
        fmd._process_face_detection = MagicMock()
        fmd._process_face_detection.return_value = 0.8

        mp_result = 0
        image = np.zeros((10,10,3))

        fmd.standardize(mp_result, image)
        
        fmd._process_kps.assert_called()
        fmd._check_framing.assert_called()
        fmd._expand_bbox.assert_called()
        fmd._get_yaw.assert_called()
        fmd._get_pitch.assert_called()
        fmd._process_face_detection.assert_called()

class TestFaceMesh(unittest.TestCase):
    @patch("mediapipe.solutions.face_mesh.FaceMesh")
    @patch("src.model.face_mesh.FaceMeshDetection")
    def test_detect(self, facemesh, fmd):
        facemesh = FaceMesh()
        facemesh.detector = MagicMock()
        facemesh.detector.return_value = MagicMock()
        facemesh.detector.return_value.process = MagicMock()
        facemesh.detector.return_value.process.return_value = 0

        fmd.return_value = MagicMock()
        fmd.return_value.standardize = MagicMock()

        result = facemesh.detect(1)
        facemesh.detector.process.assert_called()


        
