import os
import shutil
import argparse

def move_video_folder(video_path, label, dataset_root):

    if label == '1':
        destination_folder = os.path.join(dataset_root,'test/0-real')
    elif label == '0':
        destination_folder = os.path.join(dataset_root,'test/1-fake')
    else:
        return

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    if os.path.exists(video_path):
        print(f"Moving {video_path} to {destination_folder}")
        shutil.move(video_path, destination_folder)
    
   

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move video folders based on labels")
    parser.add_argument("file_path", type=str, help="Path to the text file")
    parser.add_argument("dataset_root", type=str, help="Path to the root of the celebdf dataset")
    args = parser.parse_args()

    file_path = args.file_path
    dataset_root = args.dataset_root

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            label, video_path = line.split(' ', 1)
            video_path = video_path.split(".mp4")[0]
            video_path = os.path.join(dataset_root, video_path)
            move_video_folder(video_path, label, dataset_root)