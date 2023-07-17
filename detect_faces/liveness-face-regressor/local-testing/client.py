import os
import argparse
import time
import asyncio
import comm
import cv2
import base64
import numpy as np
from natsort import natsorted


def decode_b64(image):
    buf_decode = base64.b64decode(image)
    return decode_bin(buf_decode)


def decode_bin(_bytes):
    nparr = np.fromstring(_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)


# Test code
def draw_keypoints_bbox(image, keypoints_list, bbox, output_path):
    idx_lst = [0, 27, 16, 1, 28, 15]
    for i, keypoint in enumerate(keypoints_list):
        if i in idx_lst:
            coordinates = (int(keypoint[0]), int(keypoint[1]))
            image = cv2.circle(
                image, coordinates, radius=3, color=(255, 0, 0), thickness=-1
            )

    image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

    cv2.imwrite(output_path, image)


def draw_text_keypoints_bbox(image, keypoints_list, bbox, output_path):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.3
    color = (255, 0, 0)
    thickness = 1
    for i, keypoint in enumerate(keypoints_list):
        coordinates = (int(keypoint[0]), int(keypoint[1]))
        image = cv2.putText(
            image, str(i), coordinates, font, fontScale, color, thickness, cv2.LINE_AA
        )

    image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

    cv2.imwrite(output_path, image)


async def request_old_face(frames_list):
    server_port = os.environ.get("PORT", 4011)
    server_url = os.environ.get(
        "SERVER_URL", "http://localhost:{}/regress-face".format(server_port)
    )

    communicator = comm.FaceRegressorComm(server_url, "old face comm")

    start = time.time()
    r = await communicator.get_images_roi(frames_list, "foo")
    end = time.time()
    import pdb

    pdb.set_trace()
    print("Elapsed time was {}".format(end - start))
    print("Drawing...")
    for i, (img, keypoints, bbox) in enumerate(zip(r.images_n, r.keypoints, r.bboxes)):
        draw_keypoints_bbox(
            decode_b64(img), keypoints, bbox, "results/out{}_old.jpg".format(i)
        )


async def request_new_face(frames_list):
    server_port = os.environ.get("PORT", 4011)
    server_url = os.environ.get(
        "SERVER_URL", "http://localhost:{}/regress-face".format(server_port)
    )

    communicator = comm.NewFaceRegressorComm(server_url, "new face comm")
    start = time.time()
    r = await communicator.get_images_roi(frames_list, "foo")
    end = time.time()
    print("Elapsed time was {}".format(end - start))
    print("Drawing...")
    if not os.path.isdir("results"):
        os.mkdir("results")
    for i, (img, keypoints, bbox) in enumerate(zip(r.images_n, r.keypoints, r.bboxes)):
        draw_keypoints_bbox(
            decode_b64(img), keypoints, bbox, "results/out{}_new.jpg".format(i)
        )


async def main():

    parser = argparse.ArgumentParser(description="Test Client for face regressor")
    parser.add_argument("-f", "--files")
    parser.add_argument("--new-face", default=False, action="store_true")
    args = parser.parse_args()
    frames_list = []

    for root, dirs, files in os.walk(args.files):
        files = natsorted(files)
        for _file in files:
            img_fp = os.path.join(root, _file)
            frames_list.append(("images", open(img_fp, "rb")))

    if args.new_face:
        await request_new_face(frames_list)
    else:
        await request_old_face(frames_list)


if __name__ == "__main__":
    asyncio.run(main())
