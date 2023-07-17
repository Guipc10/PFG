from typing import List
import argparse
import time
import os
import cv2
import numpy as np
from import_facemesh import face_mesh
import pdb


def crop_faces(root_dir: str, output_dir: str) -> None:
    img_lst = [file for file in os.listdir(root_dir) if file.endswith(".jpg")]

    for img in img_lst:
        try:
            img_path = os.path.join(root_dir, img)
            image = cv2.imread(img_path)
            if image is not None:
                detections = face_mesh.detect(image)
                if detections["conf_score"] >= 0.5:
                    bbox = detections["bbox"]
                    bbox_x_min = bbox[0]
                    bbox_y_min = bbox[1]
                    bbox_x_max = bbox[2]
                    bbox_y_max = bbox[3]

                    cropped_image = image[bbox_y_min:bbox_y_max, bbox_x_min:bbox_x_max]
                    if np.any(cropped_image):
                        output_path = os.path.join(output_dir, img)
                        cv2.imwrite(output_path, cropped_image)

        except:
            import pdb

            pdb.set_trace()


def main():
    parser = argparse.ArgumentParser(
        description="Gest best frame from liveness datasets videos, must run outside the folder best_frame"
    )
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        help="Path to folder with images to be cropped",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to output folder to save cropped images",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    start = time.time()
    crop_faces(args.data, args.output)
    end = time.time()
    print(f"Total elapsed time: {end-start} seconds")


if __name__ == "__main__":
    main()
