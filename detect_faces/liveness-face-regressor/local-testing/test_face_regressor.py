import requests
import json
import os, sys
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)


# setting up server variables
SERVER_PORT = os.environ.get("FACE_REGRESSOR_PORT", 4010)
SERVER = os.environ.get("FACE_REGRESSOR_URL", "http://internal.dev.mostqi.com.br")
SERVER_URL = "{}:{}/regress-face".format(SERVER, SERVER_PORT)
# SERVER_URL = "http://192.168.0.45:4010/regress-face" #local server

# setting up path variables
TEST_JSONS_PATH = "results/testing"
GROUND_TRUTH_JSONS_PATH = "results/ground_truth"
TRUE_PATH = r"dados/testes_movimento/reais/"
FRAUD_PATH = r"dados/testes_movimento/fraudes/"


class TestFaceRegressor:
    def get_test_list():
        """
        Build a testing list, each element of the list is a tuple with base file path,
        directory with image and image path.
        """
        if not os.path.exists(TEST_JSONS_PATH):
            os.makedirs(TEST_JSONS_PATH)

        test_list = []
        for base_files_path in [TRUE_PATH, FRAUD_PATH]:
            dirs = os.listdir(base_files_path)
            dirs = [
                x for x in dirs if os.path.isdir(r"{}{}".format(base_files_path, x))
            ]

            for directory in dirs:
                img_paths = [
                    x
                    for x in os.listdir(r"{}{}".format(base_files_path, directory))
                    if x.endswith(".jpg") or x.endswith(".png")
                ]

                for image_path in img_paths:
                    test_list.append((base_files_path, directory, image_path))
        return test_list

    def compare_with_ground_truth(self, test_json, filename):
        """
        Compares ground truth json with a given test json.
        If ROI coordinates differ only by around 5%, test json is approved.
        """
        filepath = GROUND_TRUTH_JSONS_PATH + "/" + filename
        with open(filepath) as json_file:
            gt_json = json.load(json_file)

        print("COMPARING {}".format(filename))
        print(
            "top_left: \n\tGT:\t {} \n\tTest:\t {}".format(
                gt_json["top_left"], test_json["top_left"]
            )
        )
        print(
            "bottom_right: \n\tGT:\t {} \n\tTest:\t {}".format(
                gt_json["bottom_right"], test_json["bottom_right"]
            )
        )

        test_json["cmp_top_left_x"] = max(
            gt_json["top_left"][0], test_json["top_left"][0]
        ) / min(gt_json["top_left"][0], test_json["top_left"][0])
        test_json["cmp_top_left_y"] = max(
            gt_json["top_left"][1], test_json["top_left"][1]
        ) / min(gt_json["top_left"][1], test_json["top_left"][1])
        test_json["cmp_bottom_right_x"] = max(
            gt_json["bottom_right"][0], test_json["bottom_right"][0]
        ) / min(gt_json["bottom_right"][0], test_json["bottom_right"][0])
        test_json["cmp_bottom_right_y"] = max(
            gt_json["bottom_right"][1], test_json["bottom_right"][1]
        ) / min(gt_json["bottom_right"][1], test_json["bottom_right"][1])

        cond1 = (
            test_json["cmp_top_left_x"] >= 0.95 and test_json["cmp_top_left_x"] <= 1.05
        )
        cond2 = (
            test_json["cmp_top_left_y"] >= 0.95 and test_json["cmp_top_left_y"] <= 1.05
        )
        cond3 = (
            test_json["cmp_bottom_right_x"] >= 0.95
            and test_json["cmp_bottom_right_x"] <= 1.05
        )
        cond4 = (
            test_json["cmp_bottom_right_y"] >= 0.95
            and test_json["cmp_bottom_right_y"] <= 1.05
        )

        test_json["approved"] = True if (cond1 and cond2 and cond3 and cond4) else False

        print("\n\n")
        assert cond1 and cond2 and cond3 and cond4
        return test_json

    @pytest.mark.parametrize("base_files_path,directory,image_path", get_test_list())
    def test(self, base_files_path, directory, image_path):
        """
        For each image on base files path get the ROI coordinates and compare with ground truth,
        testing it, then save.
        """
        print("{}{}/{}".format(base_files_path, directory, image_path))

        filepath = "{}{}/{}".format(base_files_path, directory, image_path)
        with open(filepath, "rb") as img_file:
            img_file_read = img_file.read()
            r = requests.post(SERVER_URL, files={"images": img_file_read})
            for dict_ in r.json():
                for img_from_fr in dict_["images"]:
                    if img_from_fr is not None:
                        to_save = img_from_fr[2]
                        to_save["path"] = "{}/{}".format(directory, image_path)

                        filename = "{}/{}.json".format(
                            TEST_JSONS_PATH, directory + "_" + image_path
                        )
                        to_save = self.compare_with_ground_truth(
                            to_save, directory + "_" + image_path + ".json"
                        )
                        with open(filename, "w") as json_file:
                            json.dump(to_save, json_file, indent=4)
