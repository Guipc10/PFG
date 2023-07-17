# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath(''))

import unittest

from  src.model.util.arguments import ServerArgs
# Patch
class TestServerArgs(unittest.TestCase):
    def setUp(self): 
        os.environ.pop("KPS_MAPPING_FILE", None)
        os.environ.pop("LEFT_EYE_KPS_FILE", None)
        os.environ.pop("RIGHT_EYE_KPS_FILE", None)
        os.environ.pop("NOSE_KPS_FILE", None)
        os.environ.pop("MOUTH_KPS_FILE", None)
        os.environ.pop("BBOX_RESIZE_FACTOR", None)
        os.environ.pop("SCALE_PITCH_FACTOR", None)
        self.server_args = ServerArgs()

    def test_default_values(self):
        # Test default values of ServerArgs
        self.assertEqual(self.server_args.kps_mapping_file, "src/model/util/kps_mapping.txt")
        self.assertEqual(self.server_args.left_eye_kps, "src/model/util/left_eye_kps.txt")
        self.assertEqual(self.server_args.right_eye_kps, "src/model/util/right_eye_kps.txt")
        self.assertEqual(self.server_args.nose_kps, "src/model/util/nose_kps.txt")
        self.assertEqual(self.server_args.mouth_kps, "src/model/util/mouth_kps.txt")
        self.assertEqual(self.server_args.bbox_resize_factor, 1.5)
        self.assertEqual(self.server_args.scale_pitch_factor, 1.4)

    def test_environment_variables(self):
        # Test setting environment variables
        os.environ["KPS_MAPPING_FILE"] = "src/model/util/kps_mapping_alternative.txt"
        os.environ["LEFT_EYE_KPS_FILE"] = "src/model/util/left_eye_kps_alternative.txt"
        os.environ["RIGHT_EYE_KPS_FILE"] = "src/model/util/right_eye_kps_alternative.txt"
        os.environ["NOSE_KPS_FILE"] = "src/model/util/nose_kps_alternative.txt"
        os.environ["MOUTH_KPS_FILE"] = "src/model/util/mouth_kps_alternative.txt"
        os.environ["BBOX_RESIZE_FACTOR"] = "1.8"
        os.environ["SCALE_PITCH_FACTOR"] = "1.6"

        server_args = ServerArgs()
        self.assertEqual(server_args.kps_mapping_file, "src/model/util/kps_mapping_alternative.txt")
        self.assertEqual(server_args.left_eye_kps, "src/model/util/left_eye_kps_alternative.txt")
        self.assertEqual(server_args.right_eye_kps, "src/model/util/right_eye_kps_alternative.txt")
        self.assertEqual(server_args.nose_kps, "src/model/util/nose_kps_alternative.txt")
        self.assertEqual(server_args.mouth_kps, "src/model/util/mouth_kps_alternative.txt")
        self.assertEqual(server_args.bbox_resize_factor, 1.8)
        self.assertEqual(server_args.scale_pitch_factor, 1.6)

if __name__ == '__main__':
    # Run the tests
    unittest.main()    


