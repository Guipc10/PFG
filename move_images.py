import os
import shutil
import argparse
import pdb


def move_and_rename_files(given_input, current_directory):
    # Get a list of all directories in the current directory
    directories = [
        name
        for name in os.listdir(current_directory)
        if os.path.isdir(os.path.join(current_directory, name))
    ]

    # Iterate through each directory
    for directory in directories:
        # Get the list of .jpg files in the directory
        file_list = [
            file
            for file in os.listdir(os.path.join(current_directory, directory))
            if file.lower().endswith(".jpg")
        ]

        # Iterate through each .jpg file
        for file_name in file_list:
            # Generate the new name for the file
            new_name = given_input + "_" + directory + "_" + file_name

            # Build the source and destination paths
            source_path = os.path.join(current_directory, directory, file_name)
            destination_path = os.path.join(current_directory, new_name)

            # Move and rename the file
            shutil.move(source_path, destination_path)
            print(f"Moved and renamed: {file_name} -> {new_name}")

        if not os.listdir(os.path.join(current_directory, directory)):
            os.rmdir(os.path.join(current_directory, directory))
            print(
                f"Deleted empty directory: {os.path.join(current_directory, directory)}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Move and rename .jpg files in directories."
    )
    parser.add_argument("--dataset_name", "-d", type=str, help="The given input string")
    parser.add_argument(
        "--current_directory",
        "-c",
        type=str,
        default=os.getcwd(),
        help="The current directory (optional)",
    )

    args = parser.parse_args()

    move_and_rename_files(args.dataset_name, args.current_directory)
