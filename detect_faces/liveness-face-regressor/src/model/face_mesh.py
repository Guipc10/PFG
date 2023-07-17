import cv2
import mediapipe as mp
import logging
import numpy as np
from typing import List
from src.model.util.arguments import ServerArgs
from src.model.util.utils import Utils

args = ServerArgs()
logger = logging.getLogger("FaceMesh")


class FaceMeshDetection(object):
    """
    Class to represent and post process the results got from mediapipe facemesh
    """

    # Index to get 68 landmarks from the 478 got from mediapipe
    with open(args.kps_mapping_file, "r") as file:
        POINTS_478_TO_68 = [int(val) for val in file.readlines()]

    # eyes, nose and mouth indexes
    with open(args.left_eye_kps, "r") as file:
        LEFT_EYE_IDXS = [int(val) for val in file.readlines()]

    with open(args.right_eye_kps, "r") as file:
        RIGHT_EYE_IDXS = [int(val) for val in file.readlines()]

    with open(args.nose_kps, "r") as file:
        NOSE_IDXS = [int(val) for val in file.readlines()]

    with open(args.mouth_kps, "r") as file:
        MOUTH_IDXS = [int(val) for val in file.readlines()]

    def __init__(self):
        self.keypoints_68: List[tuple] = None
        self.keypoints_478: List[tuple] = None
        self.yaw: float = None
        self.pitch: float = None
        self.bbox: List[int] = None
        self.correctly_framed: bool = None
        self.conf_score: float = None

    def _expand_bbox(self, bbox):
        """
        Expand the bbox size by the given resize factor
        This is made because the bbox got from the landmarks is too small
        """
        if bbox is None:
            return None

        xmin, ymin, xmax, ymax = bbox

        bbox_width = xmax - xmin
        bbox_height = ymax - ymin
        bbox_size = max(bbox_height, bbox_width)

        center_x = (xmax + xmin) / 2
        center_y = (ymax + ymin) / 2

        new_bbox_size = bbox_size * args.bbox_resize_factor

        new_xmin = center_x - (new_bbox_size / 2)
        new_xmax = center_x + (new_bbox_size / 2)
        new_ymin = center_y - (new_bbox_size / 2)
        new_ymax = center_y + (new_bbox_size / 2)

        new_bbox = [
            int(round(new_xmin)),
            int(round(new_ymin)),
            int(round(new_xmax)),
            int(round(new_ymax)),
        ]
        return new_bbox

    def _process_kps(self, mp_result, img_height, img_width):
        """
        Get the 478 landmarks from mediapipe, convert it to 68
        and get the bbox coordinates from the min and max x,y
        coordinates from all the landmarks
        """
        if not mp_result.multi_face_landmarks:
            return None, None, None

        # Get index 0 because only one face is expected
        keypoints_478_mp = mp_result.multi_face_landmarks[0].landmark
        keypoints_478 = np.array(
            [
                [
                    int(round(landmark.x * img_width)),
                    int(round(landmark.y * img_height)),
                    int(round(landmark.z * img_width)),
                ]
                for landmark in keypoints_478_mp
            ]
        )

        keypoints_68 = keypoints_478[FaceMeshDetection.POINTS_478_TO_68]

        cx_min = keypoints_478[:, 0].min()
        cy_min = keypoints_478[:, 1].min()
        cx_max = keypoints_478[:, 0].max()
        cy_max = keypoints_478[:, 1].max()
        bbox = [cx_min, cy_min, cx_max, cy_max]

        return keypoints_478, keypoints_68, bbox

    def _check_framing(self, keypoints_68, img_height, img_width):
        """
        Check whether the eyes, nose and mouth are correctly inside
        the image limits, returns True if it is and False otherwise
        """
        if keypoints_68 is None:
            return None

        key_idxs = (
            FaceMeshDetection.LEFT_EYE_IDXS
            + FaceMeshDetection.RIGHT_EYE_IDXS
            + FaceMeshDetection.NOSE_IDXS
            + FaceMeshDetection.MOUTH_IDXS
        )

        exceeds_limits = (
            (keypoints_68[key_idxs, :2] < 0).any()
            or (keypoints_68[key_idxs, 0] > img_width).any()
            or (keypoints_68[key_idxs, 1] > img_height).any()
        )
        correctly_framed = not exceeds_limits
        return correctly_framed

    def _get_yaw(self, keypoints_68):
        """
        Estimate yaw from the landmarks 0,27 and 16
        """
        if keypoints_68 is None:
            return None

        point_0 = keypoints_68[0, :2]
        point_27 = keypoints_68[27, :2]
        point_16 = keypoints_68[16, :2]

        line_A = Utils.distance_yaw(point_0, point_27)
        line_B = Utils.distance_yaw(point_27, point_16)

        if line_A == line_B:
            return 0
        elif line_A < line_B:
            return np.arcsin(1 - (line_A / line_B))
        else:
            return -np.arcsin(1 - (line_B / line_A))

    def _get_pitch(self, keypoints_68):
        """
        Estimate pitch from the landmarks 1,28 and 15
        """
        if keypoints_68 is None:
            return None

        point_1 = keypoints_68[1]
        point_28 = keypoints_68[28]
        point_15 = keypoints_68[15]

        vertical_dist = np.cross(
            point_15[:2] - point_1[:2], point_28[:2] - point_1[:2]
        ) / np.linalg.norm(point_15[:2] - point_1[:2])
        # Uses the 3D coordinates so it is not sensible to yaw variation
        line_A = Utils.euclidean_distance(point_1, point_28)
        line_B = Utils.euclidean_distance(point_28, point_15)

        theta_1 = np.arcsin(np.clip(args.scale_pitch_factor*(vertical_dist / line_A), -1, 1))
        theta_2 = np.arcsin(np.clip(args.scale_pitch_factor*(vertical_dist / line_B), -1, 1))

        return (theta_1 + theta_2) / 2

    def _process_face_detection(self, mp_result):
        """
        Get confidence score from face detection
        """
        if not mp_result.face_detections:
            return 0.0

        # Get index 0 because only one face is expected
        detection = mp_result.face_detections[0]

        return detection.score[0]

    def standardize(self, mp_result, image):
        h, w = image.shape[0], image.shape[1]

        # Get bbox from keypoints because it's more reliable
        self.keypoints_478, self.keypoints_68, self.bbox = self._process_kps(
            mp_result, h, w
        )
        self.correctly_framed = self._check_framing(self.keypoints_68, h, w)

        self.bbox = self._expand_bbox(self.bbox)
        self.yaw = self._get_yaw(self.keypoints_68)
        self.pitch = self._get_pitch(self.keypoints_68)

        if self.keypoints_478 is not None:
            self.keypoints_478 = self.keypoints_478.tolist()
            self.keypoints_68 = self.keypoints_68.tolist()

        self.conf_score = self._process_face_detection(mp_result)
        if not self.bbox:
            self.conf_score = 0.0

class FaceMesh(object):
    """
    Class that instantiates the Mediapipe FaceMesh model, that does the face
    detection and landmarks extraction. Runs on CPU.

    Parameters
    ----------
        max_num_faces:
            Maximum number of faces to detect
        min_detection_confidence:
            Minimum confidence value ([0.0, 1.0]) from the face detection model for the detection to be considered successful
        static_image_mode:
            If set to true, face detection runs on every input image. Default to true because tests with false showed poor results
        refine_landmarks:
            Refine landmarks around eyes and lips, default to false to save inference time
    """

    def __init__(
        self,
        max_num_faces=1,
        min_detection_confidence=0,
        static_image_mode=True,
        refine_landmarks=False,
    ): # pragma: no cover
        self.detector = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
        )

    def detect(self, img): 
        results = self.detector.process(img)
        detection = FaceMeshDetection()
        detection.standardize(results, img)

        return vars(detection)


def draw_keypoints_bbox(image, keypoints_list, bbox, output_path): # pragma: no cover

    for keypoint in keypoints_list:
        coordinates = (int(keypoint[0]), int(keypoint[1]))
        image = cv2.circle(
            image, coordinates, radius=3, color=(255, 0, 0), thickness=-1
        )

    image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

    cv2.imwrite(output_path, image)


def draw_keypoints_bbox_text(image, keypoints_list, bbox, output_path): # pragma: no cover
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    color = (255, 0, 0)
    thickness = 2

    for i, keypoint in enumerate(keypoints_list):
        coordinates = (int(keypoint[0]), int(keypoint[1]))
        cv2.putText(
            image, str(i), coordinates, font, fontScale, color, thickness, cv2.LINE_AA
        )

    image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

    cv2.imwrite(output_path, image)


def main(): # pragma: no cover
    # Test
    import os
    from natsort import natsorted
    detector = FaceMesh()
    
   
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    img_root = "emotion_images_from_orch"
    for i,file in enumerate(natsorted(os.listdir(img_root))):
        img_path = os.path.join(img_root, file)
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        result = detector.detect(img)
        draw_keypoints_bbox(img, result["keypoints_68"], result["bbox"], "outputs/result{}.jpg".format(i))


if __name__ == "__main__":
    main()
