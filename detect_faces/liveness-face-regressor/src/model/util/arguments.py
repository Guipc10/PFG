import os


class ServerArgs(object):
    def __init__(self):
        self.kps_mapping_file = os.environ.get(
            "KPS_MAPPING_FILE", "src/model/util/kps_mapping.txt"
        )
        self.left_eye_kps = os.environ.get(
            "LEFT_EYE_KPS_FILE", "src/model/util/left_eye_kps.txt"
        )
        self.right_eye_kps = os.environ.get(
            "RIGHT_EYE_KPS_FILE", "src/model/util/right_eye_kps.txt"
        )
        self.nose_kps = os.environ.get("NOSE_KPS_FILE", "src/model/util/nose_kps.txt")
        self.mouth_kps = os.environ.get(
            "MOUTH_KPS_FILE", "src/model/util/mouth_kps.txt"
        )


        self.bbox_resize_factor = float(os.environ.get("BBOX_RESIZE_FACTOR", 1.5))
        self.scale_pitch_factor = float(os.environ.get("SCALE_PITCH_FACTOR", 1.4))

