import cv2
import mediapipe as mp
from shapely.geometry import Polygon


class Palm(object):
    def __init__(self, kps=[]):
        self._kps = kps
        self._poly = None
        if self._kps:
            self._poly = Polygon(self._kps)

    def get_polygon(self):
        return self._poly

    def get_kps(self):
        return self._kps


class PalmDetector(object):
    def __init__(
        self, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5
    ):
        self.detector = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self.PALM_IDXS = [0, 4, 8, 12, 16, 20]

    def detect(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, _ = img.shape
        results = self.detector.process(img).multi_hand_landmarks

        if not results:
            return list()

        palms = list()
        for hand_landmarks in results:
            palm_kps = list()
            for idx, lmk in enumerate(hand_landmarks.landmark):
                if idx in self.PALM_IDXS:
                    palm_kps.append((lmk.x * w, lmk.y * h))
            palms.append(Palm(kps=palm_kps))

        return palms


def main():  # pragma: no cover

    img = cv2.imread(
        "/home/rafaelv/liveness-face-regressor/error/frame_0.jpg", cv2.IMREAD_UNCHANGED
    )
    detector = PalmDetector()
    detector.detect(img)
    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    main()
