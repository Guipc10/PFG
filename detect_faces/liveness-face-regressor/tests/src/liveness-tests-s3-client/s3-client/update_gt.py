import boto3
import zipfile
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('update_gt')


class UpdateGT:
    def __init__(self, gt_folder="liveness_tests", test_folder="liveness_tests_results"):
        self.gt_folder = gt_folder
        self.test_folder = test_folder

    def get_diffs(self):
        sources = []
        for path, dirs, files in os.walk(self.test_folder):
            if any(['.json' in x for x in files]):
                tmp_sources = [os.path.join(path, file) for file in files]
                sources += tmp_sources
        logger.info("Found {} diffs.".format(len(sources)))
        return sources

    def move_diffs_to_gt(self):
        '''
            Moves each .json found on self.test_folder to self.gt_folder
        '''
        sources = self.get_diffs()
        
        for src in sources:
            dest = src.replace(self.test_folder, self.gt_folder)
            os.rename(src, dest)
            logger.info("updated {}".format(dest))
            