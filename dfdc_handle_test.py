import argparse
import os
import random
import pdb
import json
import shutil

random.seed(42)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean dfdc test set by removing aumentated data and moving real/fake videos to respective folder"
    )
    parser.add_argument(
        "--main_folder", "-m", type=str, help="Path to the DFDC test folder"
    )
    parser.add_argument("--json", "-j", type=str, help="Path to the .json")
    parser.add_argument("--output", "-o", type=str, help="Path to the output folder")
    args = parser.parse_args()

    main_folder = args.main_folder
    json_file = args.json
    output_folder = args.output

    output_real = os.path.join(output_folder, "real")
    if not os.path.exists(output_real):
        os.makedirs(output_real)
    output_fake = os.path.join(output_folder, "fake")
    if not os.path.exists(output_fake):
        os.makedirs(output_fake)

    with open(json_file, "r") as file:
        test_json = json.load(file)

    for key, item in test_json.items():
        video_path = os.path.join(main_folder, key.split(".mp4")[0])
        augmentations = item["augmentations"]
        if augmentations != {}:
            continue
        if item["is_fake"] == 1:
            video_new_path = output_fake
        else:
            video_new_path = output_real
        pdb.set_trace()
        shutil.move(video_path, video_new_path)
