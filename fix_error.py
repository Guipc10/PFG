import argparse
import os
import random
from typing import List, Tuple
import shutil
import pdb
import pickle

random.seed(42)


def read_list_from_pickle(file_path):
    file = open(file_path, "rb")
    my_list = pickle.load(file)
    file.close()
    return my_list


def fix_error(dataset_path):
    deepfakes_videos_root = os.path.join(
        dataset_path, "manipulated_sequences", "Deepfakes", "c23", "videos"
    )
    faceshifter_videos_root = os.path.join(
        dataset_path, "manipulated_sequences", "FaceShifter", "c23", "videos"
    )
    faceswap_videos_root = os.path.join(
        dataset_path, "manipulated_sequences", "FaceSwap", "c23", "videos"
    )
    real_videos_root = os.path.join(
        dataset_path, "original_sequences", "youtube", "c23", "videos"
    )
    train_folder = os.path.join(dataset_path, "train")
    if not os.path.isdir(train_folder):
        os.makedirs(train_folder)
    real_train_folder = os.path.join(train_folder, "real")
    if not os.path.isdir(real_train_folder):
        os.makedirs(real_train_folder)
    fake_train_folder = os.path.join(train_folder, "fake")
    if not os.path.isdir(fake_train_folder):
        os.makedirs(fake_train_folder)
    val_folder = os.path.join(dataset_path, "val")
    if not os.path.isdir(val_folder):
        os.makedirs(val_folder)
    real_val_folder = os.path.join(val_folder, "real")
    if not os.path.isdir(real_val_folder):
        os.makedirs(real_val_folder)
    fake_val_folder = os.path.join(val_folder, "fake")
    if not os.path.isdir(fake_val_folder):
        os.makedirs(fake_val_folder)
    test_folder = os.path.join(dataset_path, "test")
    if not os.path.isdir(test_folder):
        os.makedirs(test_folder)
    real_test_folder = os.path.join(test_folder, "real")
    if not os.path.isdir(real_test_folder):
        os.makedirs(real_test_folder)
    fake_test_folder = os.path.join(test_folder, "fake")
    if not os.path.isdir(fake_test_folder):
        os.makedirs(fake_test_folder)

    test_individuals_youtube = read_list_from_pickle("test_individuals_youtube.pickle")

    for video in os.listdir(fake_train_folder):
        video_path = os.path.join(fake_train_folder, video)
        source_ind = video.split("_")[-1]

        if source_ind in test_individuals_youtube:
            shutil.move(video_path, fake_test_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample frames from video folders")
    parser.add_argument(
        "--main_folder", type=str, help="Path to the FaceForensics++ folder"
    )
    args = parser.parse_args()

    main_folder = args.main_folder

    fix_error(main_folder)
