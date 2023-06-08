import argparse
import os
import random
from typing import List, Tuple
import shutil
import pickle

random.seed(42)


def read_list_from_pickle(file_path):
    file = open(file_path, "rb")
    my_list = pickle.load(file)
    file.close()
    return my_list


def sample_random_percentage(input_list, percentage):
    num_items = round(len(input_list) * percentage)
    sampled_items = random.sample(
        input_list,
        num_items,
    )
    return sampled_items


def sample_train_val(
    input_list: List, p_train: float, p_val: float
) -> Tuple[List, List]:
    """Sample from input list p_train, p_val and p_test percentages
    input_list is expected to be a list of unique values
    """
    input_list_copy = input_list.copy()
    train_split = sample_random_percentage(input_list, p_train)
    input_list = list(set(input_list) - set(train_split))

    # Remaining values
    val_split = input_list
    assert round(len(val_split) / len(input_list_copy), 1) == round(p_val, 1)

    return train_split, val_split


def split_celebdf(dataset_path, p_train, p_val):
    fake_videos_root = os.path.join(dataset_path, "Celeb-synthesis")
    real_youtube_videos_root = os.path.join(dataset_path, "YouTube-real")
    real_celeb_videos_root = os.path.join(dataset_path, "Celeb-real")
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
    try:
        # SPLIT YOUTUBE REAL VIDEOS
        real_videos_youtube = [
            os.path.join(real_youtube_videos_root, video)
            for video in os.listdir(real_youtube_videos_root)
            if os.path.isdir(os.path.join(real_youtube_videos_root, video))
        ]

        (
            train_real_youtube,
            val_real_youtube,
        ) = sample_train_val(real_videos_youtube, p_train, p_val)

        for video_path in train_real_youtube:
            video_name = video_path.split("/")[-1]
            new_video_name = "youtube_" + video_name

            new_video_path = os.path.join(real_train_folder, new_video_name)
            shutil.move(video_path, new_video_path)
        for video_path in val_real_youtube:
            video_name = video_path.split("/")[-1]
            new_video_name = "youtube_" + video_name

            new_video_path = os.path.join(real_val_folder, new_video_name)
            shutil.move(video_path, new_video_path)

        # SPLIT CELEB REAL VIDEOS
        real_videos_celeb = [
            os.path.join(real_celeb_videos_root, video)
            for video in os.listdir(real_celeb_videos_root)
            if os.path.isdir(os.path.join(real_celeb_videos_root, video))
        ]

        (
            train_real_celeb,
            val_real_celeb,
        ) = sample_train_val(real_videos_celeb, p_train, p_val)

        for video_path in train_real_celeb:
            video_name = video_path.split("/")[-1]
            new_video_name = "celeb_" + video_name

            new_video_path = os.path.join(real_train_folder, new_video_name)
            shutil.move(video_path, new_video_path)

            # for video_path in val_real_celeb:
            video_name = video_path.split("/")[-1]
            new_video_name = "celeb_" + video_name

            new_video_path = os.path.join(real_val_folder, new_video_name)
            shutil.move(video_path, new_video_path)

        # SPLIT FAKE VIDEOS
        fake_videos = [
            os.path.join(fake_videos_root, video)
            for video in os.listdir(fake_videos_root)
            if os.path.isdir(os.path.join(fake_videos_root, video))
        ]

        (
            train_fake,
            val_fake,
        ) = sample_train_val(fake_videos, p_train, p_val)

        for video_path in train_fake:
            video_name = video_path.split("/")[-1]
            new_video_name = "fake_" + video_name

            new_video_path = os.path.join(fake_train_folder, new_video_name)
            shutil.move(video_path, new_video_path)

        for video_path in val_fake:
            video_name = video_path.split("/")[-1]
            new_video_name = "fake_" + video_name

            new_video_path = os.path.join(fake_val_folder, new_video_name)
            shutil.move(video_path, new_video_path)
    except:
        import pdb

        pdb.set_trace()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample frames from video folders")
    parser.add_argument(
        "--main_folder", type=str, help="Path to the FaceForensics++ folder"
    )
    parser.add_argument("--p_train", type=float, help="Train split percentage")
    parser.add_argument("--p_val", type=float, help="Val split percentage")
    args = parser.parse_args()

    main_folder = args.main_folder
    p_train = args.p_train
    p_val = args.p_val

    split_celebdf(main_folder, p_train, p_val)
