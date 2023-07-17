import shutil
import os
import argparse


def copy_images(txt_file, target_directory):
    with open(txt_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        img_path, path_dir, subject, label = line.strip().split(" ")
        if "VIDEOS_AR" in path_dir:
            splitter = "VIDEOS_AR"
        if "CASIA_SURF" in path_dir:
            splitter = "CASIA_SURF"
        if "HIFI_MASK" in path_dir:
            splitter = "HIFI_MASK"
        if "CEFA" in path_dir:
            splitter = "CEFA"
        img_filename = splitter + img_path.split(splitter)[-1].replace("/", "_")
        target_path = target_directory + "/" + img_filename
        shutil.copy2(img_path, target_path)
        print(f"Image {img_filename} copied to {target_directory}")


def main():
    parser = argparse.ArgumentParser(
        description="Test txt generated from get_best_frame.py by saving the images there to the desired output dir"
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path to the .txt file generated from get_best_frame.py",
    )
    parser.add_argument("-o", "--output_dir", type=str, help="Where to save the images")
    args = parser.parse_args()

    txt_file = args.file
    target_directory = args.output_dir

    if not os.path.isdir(target_directory):
        os.makedirs(target_directory)

    copy_images(txt_file, target_directory)


if __name__ == "__main__":
    main()
