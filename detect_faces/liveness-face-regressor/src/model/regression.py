import cv2
import numpy as np
from src.model.detect_hand import PalmDetector
from src.model.face_mesh import FaceMesh
from src.model.util.utils import Utils
from src.model.util.arguments import ServerArgs
from shapely.geometry import Polygon
from typing import List


class RegressorResponse(object):
    def __init__(self):
        self.keypoints: tuple = None
        self.keypoints_478: tuple = None
        self.yaw_lst: List[float] = None
        self.pitch_lst: List[float] = None
        self.bboxes: List[List] = None
        self.scores: List[float] = None
        self.has_obstruction: List[bool] = None
        self.correctly_framed: List[bool] = None

    def standardize(
        self,
        bboxes_lst,
        keypoints_68_lst,
        keypoints_478_lst,
        yaw_lst,
        pitch_lst,
        scores_lst,
        has_obstruction_lst,
        correctly_framed,
    ):
        self.keypoints = keypoints_68_lst
        self.keypoints_478 = keypoints_478_lst
        self.yaw_lst = yaw_lst
        self.pitch_lst = pitch_lst
        self.bboxes = bboxes_lst
        self.scores = scores_lst
        self.has_obstruction = has_obstruction_lst
        self.correctly_framed = correctly_framed


class Regressor(object):
    def __init__(self, args):
        self.args = args
        self.palm_detector = PalmDetector()
        self.face_mesh = FaceMesh()

    def _check_obstruction(self, palms_lst, bboxes):
        """
        Check if there is a hand obstruction the face by using Mediapipe's palm detector and
        checking if the bboxes of the palms and face overlap

        Parameters
        ----------
            palms_lst: List[Palm]
            bboxes: List[List[Int]]

        Output
        ------
            result_upsampled: List[Bool]
                True if there is obstruction and False otherwise
        """
        result = list()
        result_upsampled = list()
        original_len = len(bboxes)
        bboxes = [bbox for idx, bbox in enumerate(bboxes) if idx % 2 == 0]
        for idx, (palms, bbox) in enumerate(zip(palms_lst, bboxes)):
            has_intersection = False
            if bbox:
                bbox_polygon = Polygon(Utils.convert_coordinate_format(bbox))
                for palm in palms:
                    has_intersection = has_intersection | bbox_polygon.intersects(
                        palm.get_polygon()
                    )
            result.append(has_intersection)
        idxs = np.linspace(0, len(result) - 1, num=original_len)
        for idx in idxs:
            result_upsampled.append(result[int(idx)])
        return result_upsampled

    def detect(self, images, logger=None):
        """
        Detect face, facial landmarks and check hand obstruction in the given images

        Parameters
        ----------
            images: List[Bytes]

        Output
        ------
            output: vars(RegressorResponse)
        """

        images = [Utils.decode_img(image) for image in images]

        detections = [self.face_mesh.detect(image) for image in images]

        results = [
            (
                detection["conf_score"],
                detection["bbox"],
                detection["correctly_framed"],
                detection["keypoints_68"],
                detection["keypoints_478"],
                detection["yaw"],
                detection["pitch"],
            )
            for detection in detections
        ]
        (
            conf_scores,
            bboxes,
            correctly_framed,
            kps_68,
            kps_478,
            yaw_lst,
            pitch_lst,
        ) = zip(*results)

        palms_lst = [
            self.palm_detector.detect(img)
            for idx, img in enumerate(images)
            if idx % 2 == 0
        ]
        has_obstruction = self._check_obstruction(palms_lst, list(bboxes))

        output = RegressorResponse()
        output.standardize(
            bboxes,
            kps_68,
            kps_478,
            yaw_lst,
            pitch_lst,
            conf_scores,
            has_obstruction,
            correctly_framed,
        )
        return vars(output)


# Test code
def draw_keypoints_bbox(image, keypoints_list, bbox, output_path):  # pragma: no cover

    for keypoint in keypoints_list:
        coordinates = (int(keypoint[0]), int(keypoint[1]))
        image = cv2.circle(
            image, coordinates, radius=3, color=(255, 0, 0), thickness=-1
        )

    image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

    cv2.imwrite(output_path, image)


def main():  # pragma: no cover
    import argparse
    import time
    import os

    parser = argparse.ArgumentParser(description="Test regressor")
    parser.add_argument("-f", "--files")
    args_parsed = parser.parse_args()

    frames_list = []

    for root, dirs, files in os.walk(args_parsed.files):
        files.sort()
        for _file in files:
            if _file.endswith(".jpg"):
                img_fp = os.path.join(root, _file)
                print(img_fp)
                frames_list.append(cv2.imread(img_fp, cv2.IMREAD_COLOR))

    args = ServerArgs()
    detector = Regressor(args)
    start = time.time()
    result = detector.detect(frames_list)
    end = time.time()
    print("elapsed time {}".format(end - start))
    print("Exceeded frames limits:")
    print(result["correctly_framed"])
    for i, (img, kps, bboxes) in enumerate(
        zip(frames_list, result["keypoints"], result["bboxes"])
    ):
        draw_keypoints_bbox(img, kps, bboxes, "img_result{}.jpg".format(i))


if __name__ == "__main__":  # pragma: no cover
    main()
