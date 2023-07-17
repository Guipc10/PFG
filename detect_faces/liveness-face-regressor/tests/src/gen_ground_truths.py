import os
import asyncio
import json
import uuid
import logging
import importlib

s3_client = importlib.import_module("liveness-tests-s3-client.s3-client.s3_client")
comm_client = importlib.import_module("liveness-tests-s3-client.s3-client.comm_client")
cc = comm_client.CommClient()
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("outputs/gen_gt.log"), logging.StreamHandler()],
)
logger = logging.getLogger("gen_ground_truths")


class GenGroundTruth:
    def get_data(self, bc):
        """
        Downloads data from s3
        """
        bc.download()
        bc.unzip()

    def remove_data(self, bc):
        """
        Removes data downloaded from s3
        """
        bc.remove()

    def make_dirs(self, dir_path):
        """
        Implements the os.makedirs function.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def get_zip_paths(self, cc):
        """
        Gets full paths for all .zips
        """
        data_folder = cc.args.test_zips_path
        gt_folder = cc.args.gt_face_regressor_path

        zips = []
        for path, dirs, files in os.walk(data_folder):
            if any([".zip" in x for x in files]) and "reais/" in path:
                zips.append(os.path.join(path, files[0]))

                gt_instance_path = path.split("/")[-2:]  # ex: [reais_compressed, t42]
                gt_instance_path = "/".join(
                    gt_instance_path
                )  # ex: reais_compressed/t42
                gt_instance_path = os.path.join(gt_folder, gt_instance_path)
                self.make_dirs(gt_instance_path)
        return zips

    def save_json(self, json_name, imgs_roi):
        """
        Save a ground truths as an json file.
        """
        json_gt = dict(imgs_roi=imgs_roi.bboxes)
        with open(json_name, "w") as arq:
            json.dump(json_gt, arq, indent=4)

    async def build_gt(self, instance_paths, cc):
        """
        Make the requests to face_regressor and save the ground truths.
        """
        loop = asyncio.get_event_loop()
        cc.regressor_comm.set_event_loop(loop)

        for instance in instance_paths:
            try:
                request_id = uuid.uuid4().hex
                json_name = instance.replace(
                    "instances", "ground_truths/face-regressor"
                )
                json_name = json_name.replace(".zip", ".json")

                file = open(instance, "rb").read()
                images = await cc.parse_zip_file(file)
                imgs_roi = await cc.get_fr_response(images, request_id)

                self.save_json(json_name, imgs_roi)

                logger.info("Done {}, request_id: {}".format(instance, request_id))
            except:
                logger.info(
                    "----> FAIL {}, request_id: {}".format(instance, request_id)
                )


def main():
    cc = comm_client.CommClient()
    ggt = GenGroundTruth()
    # bc = s3_client.BotoClient()

    # ggt.get_data(bc)
    zips = ggt.get_zip_paths(cc)
    zips = sorted(zips)
    asyncio.run(ggt.build_gt(zips, cc))
    # ggt.remove_data(bc)


if __name__ == "__main__":
    main()
