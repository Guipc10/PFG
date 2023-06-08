import os
import argparse
import numpy as np
import pdb
from natsort import natsorted

def sample_frames(video_folder, num_frames_to_keep):
    frames = natsorted(os.listdir(video_folder))
    num_frames = len(frames)

    if num_frames <= num_frames_to_keep:
        return

    frames_to_keep = np.linspace(0, num_frames, num_frames_to_keep).astype(int)
    for i, frame in enumerate(frames):
        frame_path = os.path.join(video_folder, frame)
        if i not in frames_to_keep:
            print(f"Removing {frame_path}")
            os.remove(frame_path)

def process_videos(main_folder, num_frames_to_keep):
    for root, _, files in os.walk(main_folder):
        for file in files:
            if file.endswith(".jpg"):
                video_folder = os.path.dirname(os.path.join(root, file))
                sample_frames(video_folder, num_frames_to_keep)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample frames from video folders")
    parser.add_argument("main_folder", type=str, help="Path to the main folder")
    parser.add_argument("num_frames_to_keep", type=int, help="Number of frames to keep per video")
    args = parser.parse_args()

    main_folder = args.main_folder
    num_frames_to_keep = args.num_frames_to_keep

    process_videos(main_folder, num_frames_to_keep)