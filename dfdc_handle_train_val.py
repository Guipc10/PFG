import argparse
import os
import random
import pdb
import json
import shutil

random.seed(42)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Move dfdc train/val data to correct folders"
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

    output_train = os.path.join(output_folder, "train")
    if not os.path.exists(output_train):
        os.makedirs(output_train)
    output_val = os.path.join(output_folder, "val")
    if not os.path.exists(output_val):
        os.makedirs(output_val)

    output_train_real = os.path.join(output_train, "0-real")
    if not os.path.exists(output_train_real):
        os.makedirs(output_train_real)
    output_train_fake = os.path.join(output_train, "1-fake")
    if not os.path.exists(output_train_fake):
        os.makedirs(output_train_fake)

    output_val_real = os.path.join(output_val, "0-real")
    if not os.path.exists(output_val_real):
        os.makedirs(output_val_real)
    output_val_fake = os.path.join(output_val, "1-fake")
    if not os.path.exists(output_val_fake):
        os.makedirs(output_val_fake)

    with open(json_file, "r") as file:
        json_file = json.load(file)

    for key, item in json_file.items():
        video_path = os.path.join(main_folder, key.split(".mp4")[0])
        label = item["label"]
        set = item["set"]
        if set == "train":
            if label == "real":
                new_video_path = output_train_real
            elif label == "fake":
                new_video_path = output_train_fake
            else:
                print("Invalid label!!!")
                raise SystemExit(f"Video {key} has invalid label")
        elif set == "test":
            if label == "real":
                new_video_path = output_val_real
            elif label == "fake":
                new_video_path = output_val_fake
            else:
                print("Invalid label!!!")
                raise SystemExit(f"Video {key} has invalid label")

        pdb.set_trace()
        shutil.move(video_path, new_video_path)
