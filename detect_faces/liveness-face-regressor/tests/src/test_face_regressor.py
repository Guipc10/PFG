import requests
import json
import os
import asyncio
import importlib
import pytest
import logging
import uuid
import time

time.sleep(600)

comm_client = importlib.import_module("liveness-tests-s3-client.s3-client.comm_client")
lib_utils = importlib.import_module(
    "liveness-tests-s3-client.s3-client.src.lib.util.utils"
).Utils()
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("outputs/test.log"), logging.StreamHandler()],
)
logger = logging.getLogger("test_face_regressor")

cc = comm_client.CommClient()
TEST_ZIPS_PATH = cc.args.test_zips_path
GROUND_TRUTH_JSONS_PATH = cc.args.gt_face_regressor_path
TEST_OUTPUTS_PATH = cc.args.test_outputs_path


class TestFaceRegressor:

    # Exception lists used in the test functions to ignore some test instances
    exception_list = open("exception_list.txt").read().splitlines()

    def get_test_list(exception_list):
        """
        Returns a list of path pairs [.zip path to be tested, respective ground truth .json path] that are not in the exception list.
        """
        # reading .zip paths
        test_instances = []
        for path, dirs, files in os.walk(TEST_ZIPS_PATH):
            if (
                any([".zip" in x for x in files])
                and "fraude" not in path
                and "reais_affine" not in path
                and "reais_crop" not in path
            ):
                if not any([x in os.path.join(path, files[0]) for x in exception_list]):
                    test_instances.append(os.path.join(path, files[0]))

        # reading .json ground truths
        gt_instances = []
        for path, dirs, files in os.walk(GROUND_TRUTH_JSONS_PATH):
            if any([".json" in x for x in files]):
                gt_instances.append(os.path.join(path, files[0]))

        # building test pairs
        test_pairs = []
        for ti in test_instances:
            tmp_gt = ti.replace("instances", "ground_truths/face-regressor").replace(
                ".zip", ".json"
            )
            tmp_gt_split = tmp_gt.split("/")
            tmp_gt = (
                "/".join(tmp_gt_split[0:3])
                + "/"
                + tmp_gt_split[3].split("_")[0]
                + "/"
                + "/".join(tmp_gt_split[4:])
            )
            if tmp_gt in gt_instances:
                test_pairs.append([ti, tmp_gt])

        return sorted(test_pairs)

    def get_gt_json(self, gt_json_path):
        """
        Get and load the ground truths files.
        """
        with open(gt_json_path) as arq:
            gt_json = json.load(arq)
        return gt_json

    async def get_fr_response(self, test_zip_path, case=""):
        """
        Make the requests to the face regressor.
        """
        request_id = uuid.uuid4().hex
        logger.info("request_id: {}".format(request_id))

        if case == "empty_list" or case == None:
            images = [] if case == "empty_list" else None
            server_url = cc.args.regressor_url.format(cc.args.regressor_port)
            response = requests.post(
                server_url, files=images, headers={"Param-Request-Id": request_id}
            )
            json_gt = dict(err=response.json()[0]["err"])

        else:
            loop = asyncio.get_event_loop()
            cc.regressor_comm.set_event_loop(loop)

            file = open(test_zip_path, "rb").read()
            images = await lib_utils.parse_zip_file(file)
            imgs_roi = await cc.get_fr_response(images, request_id)
            json_gt = dict(imgs_roi=imgs_roi.bboxes)

        return json_gt

    async def get_test_json(self, test_zip_path, case=""):
        """
        Get a dict with the face regressor predictions.
        """
        test_json = await self.get_fr_response(test_zip_path, case)
        if test_json is None:
            logger.info("----> FAIL {}".format(test_zip_path))
            assert False
            return
        return test_json

    def make_dirs(self, dir_path):
        """
        Implements the os.makedirs function.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def save_json(self, test_json_filepath, test_json):
        """
        Save the face regressor predicitons as a json file.
        """
        with open(test_json_filepath, "w") as arq:
            json.dump(test_json, arq, indent=4)

    def save_diff(self, test_zip_path, test_json, save_diff_path):
        """
        Function used to save the predictions as json file for the instances that failed in the tests.
        """
        results_folder = TEST_OUTPUTS_PATH + save_diff_path
        test_zip_path_split = test_zip_path.split("/")
        subpath = "/".join(test_zip_path_split[2:-1])
        path = os.path.join(results_folder, subpath)
        test_json_filepath = os.path.join(
            path, test_zip_path_split[-1].replace(".zip", ".json")
        )
        self.make_dirs(path)
        self.save_json(test_json_filepath, test_json)

    async def compare_test_and_gt(self, test_zip_path, test_json, gt_json):
        """
        Function that do the asserts of the tests. Analyse if the instances have the expected prediciton. the test fails if the prediction falls
        outside a threshold for 20% of frames or more.
        """
        file = open(test_zip_path, "rb").read()
        images = await cc.parse_zip_file(file)

        if len(test_json["imgs_roi"]) / len(images) < 0.5:
            logger.info("Failed: {}".format(test_zip_path))
            self.save_diff(test_zip_path, test_json, save_diff_path="face_regressor")
            assert False

        if len(test_json["imgs_roi"]) == len(gt_json["imgs_roi"]):
            fail_frames = 0

            for bbox_gt, bbox_test in zip(test_json["imgs_roi"], gt_json["imgs_roi"]):
                max_d0 = ((abs(bbox_gt[0]) + abs(bbox_test[0])) / 2) * 0.50
                max_d1 = ((abs(bbox_gt[1]) + abs(bbox_test[1])) / 2) * 0.30
                max_d2 = ((abs(bbox_gt[2]) + abs(bbox_test[2])) / 2) * 0.10
                max_d3 = ((abs(bbox_gt[3]) + abs(bbox_test[3])) / 2) * 0.10

                if (
                    abs(abs(bbox_gt[0]) - abs(bbox_test[0])) > max_d0
                    or abs(abs(bbox_gt[1]) - abs(bbox_test[1])) > max_d1
                    or abs(abs(bbox_gt[2]) - abs(bbox_test[2])) > max_d2
                    or abs(abs(bbox_gt[3]) - abs(bbox_test[3])) > max_d3
                ):
                    fail_frames += 1

            if fail_frames / len(test_json["imgs_roi"]) > 0.2:
                logger.info("Failed: {}".format(test_zip_path))
                self.save_diff(
                    test_zip_path, test_json, save_diff_path="face_regressor"
                )
            assert fail_frames / len(test_json["imgs_roi"]) <= 0.2  # 20% do total

        else:
            logger.info(
                "The number os frames in prediction is different of the number of frames in the ground truth"
            )
            if "reais/" in test_zip_path:
                logger.info("Failed: {}".format(test_zip_path))
                self.save_diff(
                    test_zip_path, test_json, save_diff_path="face_regressor"
                )
                assert False

    @pytest.mark.parametrize(
        "test_zip_path,gt_json_path", get_test_list(exception_list)
    )
    @pytest.mark.asyncio
    async def test(self, test_zip_path, gt_json_path):
        """
        Main test function, tests each pair returned by get_test_list()
        """
        # getting test and ground truth jsons
        gt_json = self.get_gt_json(gt_json_path)
        test_json = await self.get_test_json(test_zip_path)
        if test_json is None:
            assert False
            return

        await self.compare_test_and_gt(test_zip_path, test_json, gt_json)

    @pytest.mark.parametrize(
        "test_zip_path,gt_json_path", get_test_list(exception_list)[0:2]
    )
    @pytest.mark.asyncio
    async def test_empty_list(self, test_zip_path, gt_json_path):
        """
        Tests instances with empty list
        """
        test_json = await self.get_test_json(test_zip_path, case="empty_list")
        if test_json is None:
            assert False
            return

        if test_json["err"] != "Empty List or None object is not acceptable":
            self.save_diff(test_zip_path, test_json, "face_regressor_empty_list")
        assert test_json["err"] == "Empty List or None object is not acceptable"

    @pytest.mark.parametrize(
        "test_zip_path,gt_json_path", get_test_list(exception_list)[0:2]
    )
    @pytest.mark.asyncio
    async def test_none(self, test_zip_path, gt_json_path):
        """
        Tests instances with None in test_zip_path
        """
        test_json = await self.get_test_json(test_zip_path, case=None)
        if test_json is None:
            assert False
            return

        if test_json["err"] != "Empty List or None object is not acceptable":
            logger.info("Failed: {}".format(test_zip_path))
            self.save_diff(test_zip_path, test_json, "face_regressor_none")
        assert test_json["err"] == "Empty List or None object is not acceptable"
