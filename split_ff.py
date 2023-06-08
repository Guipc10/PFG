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


def sample_random_percentage(input_list, percentage):
    num_items = round(len(input_list) * percentage)
    sampled_items = random.sample(
        input_list,
        num_items,
    )
    return sampled_items


def sample_train_val_test(
    input_list: List, p_train: float, p_val: float, p_test: float
) -> Tuple[List, List, List]:
    """Sample from input list p_train, p_val and p_test percentages
    input_list is expected to be a list of unique values
    """
    input_list_copy = input_list.copy()
    train_split = sample_random_percentage(input_list, p_train)
    input_list = list(set(input_list) - set(train_split))

    p_val = p_val / (1 - p_train)
    val_split = sample_random_percentage(input_list, p_val)
    input_list = list(set(input_list) - set(val_split))

    # Remaining values
    test_split = input_list
    assert round(len(test_split) / len(input_list_copy), 1) == round(p_test, 1)

    return train_split, val_split, test_split


def split_ff(dataset_path, p_train, p_val, p_test):
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

    # SPLIT YOUTUBE REAL VIDEOS
    real_videos_youtube = [
        video
        for video in os.listdir(real_videos_root)
        if os.path.isdir(os.path.join(real_videos_root, video))
    ]
    unique_individuals_youtube = list(set(real_videos_youtube))
    try:
        (
            train_individuals_youtube,
            val_individuals_youtube,
            test_individuals_youtube,
        ) = sample_train_val_test(unique_individuals_youtube, p_train, p_val, p_test)
    except:
        pdb.set_trace()

    real_videos_youtube_path = [
        os.path.join(real_videos_root, real_video_youtube)
        for real_video_youtube in real_videos_youtube
    ]
    for video_path in real_videos_youtube_path:
        video_name = video_path.split("/")[-1]
        new_video_name = "youtube_" + video_name
        individual = video_name

        if individual in train_individuals_youtube:
            split_folder = real_train_folder
        elif individual in val_individuals_youtube:
            split_folder = real_val_folder
        elif individual in test_individuals_youtube:
            split_folder = real_test_folder
        else:
            raise SystemExit(
                f"Individual {individual}, video path {video_path} not in any train, val or test splits"
            )
        new_video_path = os.path.join(split_folder, new_video_name)
        # pdb.set_trace()
        # shutil.move(video_path, new_video_path)

    # SPLIT DEEPFAKE VIDEOS
    deepfakes_videos_path = [
        os.path.join(deepfakes_videos_root, video)
        for video in os.listdir(deepfakes_videos_root)
        if os.path.isdir(os.path.join(deepfakes_videos_root, video))
    ]
    for video_path in deepfakes_videos_path:
        video_name = video_path.split("/")[-1]
        new_video_name = "deepfakes_" + video_name
        source_individual = video_name.split("_")[-1]

        if source_individual in train_individuals_youtube:
            split_folder = fake_train_folder
        elif source_individual in val_individuals_youtube:
            split_folder = fake_val_folder
        elif source_individual in test_individuals_youtube:
            split_folder = fake_train_folder
        else:
            raise SystemExit(
                f"Individual {source_individual}, video path {video_path} not in any train, val or test splits"
            )
        new_video_path = os.path.join(split_folder, new_video_name)

        # shutil.move(video_path, new_video_path)

    # SPLIT FACESHIFTER VIDEOS
    faceshifter_videos_path = [
        os.path.join(faceshifter_videos_root, video)
        for video in os.listdir(faceshifter_videos_root)
        if os.path.isdir(os.path.join(faceshifter_videos_root, video))
    ]
    for video_path in faceshifter_videos_path:
        video_name = video_path.split("/")[-1]
        new_video_name = "faceshifter_" + video_name
        source_individual = video_name.split("_")[-1]

        if source_individual in train_individuals_youtube:
            split_folder = fake_train_folder
        elif source_individual in val_individuals_youtube:
            split_folder = fake_val_folder
        elif source_individual in test_individuals_youtube:
            split_folder = fake_train_folder
        else:
            raise SystemExit(
                f"Individual {source_individual}, video path {video_path} not in any train, val or test splits"
            )
        new_video_path = os.path.join(split_folder, new_video_name)
        pdb.set_trace()
        # shutil.move(video_path, new_video_path)

    # SPLIT FACESWAP VIDEOS
    faceswap_videos_path = [
        os.path.join(faceswap_videos_root, video)
        for video in os.listdir(faceswap_videos_root)
        if os.path.isdir(os.path.join(faceswap_videos_root, video))
    ]
    for video_path in faceswap_videos_path:
        video_name = video_path.split("/")[-1]
        new_video_name = "faceswap_" + video_name
        source_individual = video_name.split("_")[-1]

        if source_individual in train_individuals_youtube:
            split_folder = fake_train_folder
        elif source_individual in val_individuals_youtube:
            split_folder = fake_val_folder
        elif source_individual in test_individuals_youtube:
            split_folder = fake_train_folder
        else:
            raise SystemExit(
                f"Individual {source_individual}, video path {video_path} not in any train, val or test splits"
            )
        new_video_path = os.path.join(split_folder, new_video_name)

        # shutil.move(video_path, new_video_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample frames from video folders")
    parser.add_argument(
        "--main_folder", type=str, help="Path to the FaceForensics++ folder"
    )
    parser.add_argument("--p_train", type=float, help="Train split percentage")
    parser.add_argument("--p_val", type=float, help="Val split percentage")
    parser.add_argument("--p_test", type=float, help="Test split percentage")
    args = parser.parse_args()

    main_folder = args.main_folder
    p_train = args.p_train
    p_val = args.p_val
    p_test = args.p_test

    split_ff(main_folder, p_train, p_val, p_test)
