import os
import importlib

import sys

# Append the desired path to PYTHONPATH
sys.path.append('/app/liveness-face-regressor')

os.environ["KPS_MAPPING_FILE"] = "liveness-face-regressor/src/model/util/kps_mapping.txt"
os.environ["LEFT_EYE_KPS_FILE"] = "liveness-face-regressor/src/model/util/left_eye_kps.txt"
os.environ["RIGHT_EYE_KPS_FILE"] = "liveness-face-regressor/src/model/util/right_eye_kps.txt"
os.environ["NOSE_KPS_FILE"] = "liveness-face-regressor/src/model/util/nose_kps.txt"
os.environ["MOUTH_KPS_FILE"] = "liveness-face-regressor/src/model/util/mouth_kps.txt"


module = importlib.import_module("liveness-face-regressor.src.model.face_mesh")
face_mesh = module.FaceMesh()