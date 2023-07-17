import cv2
import numpy as np
import logging
import base64
from io import BytesIO

logger = logging.getLogger("Utils")


class Utils(object):
    @staticmethod
    def convert_coordinate_format(bbox):
        """
        Convert coordinates format from
        [xmin, ymin, xmax, ymax]
        to
        [(tl.x,tl.y), (tr.x,tr.y), (br.x, br.y), (bl.x, bl.y)]
        """
        bbox = [int(x) for x in bbox]
        xmin, ymin, xmax, ymax = bbox
        tl = (xmin, ymax)
        tr = (xmax, ymax)
        br = (xmax, ymin)
        bl = (xmin, ymin)

        return [tl, tr, br, bl]

    @staticmethod
    def crop_img(img, roi_box):
        if not roi_box:
            return img
        h, w = img.shape[:2]

        sx, sy, ex, ey = [int(round(_)) for _ in roi_box]
        dh, dw = ey - sy, ex - sx
        if len(img.shape) == 3:
            res = np.zeros((dh, dw, 3), dtype=np.uint8)
        else:
            res = np.zeros((dh, dw), dtype=np.uint8)
        if sx < 0:
            sx, dsx = 0, -sx
        else:
            dsx = 0

        if ex > w:
            ex, dex = w, dw - (ex - w)
        else:
            dex = dw

        if sy < 0:
            sy, dsy = 0, -sy
        else:
            dsy = 0

        if ey > h:
            ey, dey = h, dh - (ey - h)
        else:
            dey = dh

        res[dsy:dey, dsx:dex] = img[sy:ey, sx:ex]
        return res

    @staticmethod
    def distance_yaw(point_a, point_b):
        """
        Calculates the euclidean distance to get the yaw from the landmarks
        The calculation is a little different from usual euclidean distance
        because its assumed that point B must be on the left size of the point A,
        otherwise the distance is set to 0. This is important when the facial landmarks
        are 2D projections of 3D landmarks
        """
        if point_b[0] < point_a[0]:
            return 0

        return np.sqrt(np.sum((point_a - point_b) ** 2))

    @staticmethod
    def euclidean_distance(point_a, point_b):
        """
        Usual Euclidean Distance considering only x,y coordinates
        """
        return np.sqrt(np.sum((point_a - point_b) ** 2))

    @staticmethod
    def encode_img_b(img):
        _, buf = cv2.imencode(".png", img)
        return base64.b64encode(buf)

    @staticmethod
    def decode_img(np_bytes):  # pragma: no cover
        load_bytes = BytesIO(np_bytes)
        loaded_np = np.load(load_bytes, allow_pickle=False)
        return loaded_np
