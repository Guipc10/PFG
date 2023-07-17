import asyncio
import importlib
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentdir)
import src.lib.communications.comm as comm
from src.lib.util.arguments import TestArgs
from zipfile import ZipFile
from io import BytesIO
import re


class CommClient:
    def __init__(self):
        self.args = TestArgs()

        self.regressor_comm = comm.FaceRegressorComm(
            self.args.regressor_url.format(self.args.regressor_port),
            "face_regressor"
        )

        self.pose_estimation_comm = comm.PoseEstimationComm(
            self.args.inference_url.format(self.args.inference_port),
            "pose_estimation"
        )
    
        self.ar_comm = comm.ActionRecognitionComm(
            self.args.action_recognition_url.format(
                self.args.action_recognition_port
            ),
            "action_recognition"
        )

        self.ec_comm = comm.EmotionClassificationComm(
            self.args.emotion_classification_url.format(
                self.args.emotion_classification_port
            ),
            "emotion_classification"
        )

    def natural_sort(self, l): 
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(l, key = alphanum_key)

    async def parse_zip_file(self, file):
        images = []
        zipfile = ZipFile(BytesIO(file))
        for name in self.natural_sort(zipfile.namelist()):
            if name.lower().endswith((".jpg", ".png", ".tiff", ".tif")):
                images.append(zipfile.read(name))
        return images

    async def get_params(self, images, request_id):
        response_fr = await asyncio.create_task(
            self.regressor_comm.get_fr_response(images, request_id)
        )
        response_pe = await asyncio.create_task(
            self.pose_estimation_comm.get_poses(response_fr.images, request_id)
        )
        return response_pe, response_fr
        
    async def get_fr_response(self, images, request_id):
        response_fr = await asyncio.create_task(
            self.regressor_comm.get_fr_response(images, request_id)
        )
        return response_fr

    async def get_ar(self, images, request_id):
        response_ar = await asyncio.create_task(
            self.ar_comm.get_ar(images, request_id)
        )
        return response_ar

    async def get_ec(self, images, request_id, bboxes):
        response_ec = await asyncio.create_task(
            self.ec_comm.get_ec(images, request_id, bboxes)
        )
        return response_ec