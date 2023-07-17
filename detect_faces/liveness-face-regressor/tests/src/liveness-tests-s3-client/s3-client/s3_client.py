import boto3
import zipfile
import os
import shutil
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('s3_client')


class BotoClient:
    def __init__(self, bucket_name='mostqi-liveness-tests', s3_file='liveness_tests.zip', 
                 local_file='liveness_tests.zip'):
        self.bucket_name = bucket_name
        self.s3_file = s3_file
        self.local_file = local_file
        self.s3 = boto3.resource('s3')
        
    def download(self):
        logger.info('downloading...')
        if not os.path.exists(self.local_file):
            self.s3.Bucket(self.bucket_name).download_file(self.s3_file, self.local_file)
        
    def unzip(self, path_to_extract='./'):
        logger.info('unzipping...')
        with zipfile.ZipFile(self.local_file, 'r') as zip_ref:
            zip_ref.extractall(path_to_extract)
        
    def remove(self, file_path='./liveness_tests'):
        logger.info('removing...')
        zip_path = '{}.zip'.format(file_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(file_path):
            shutil.rmtree(file_path)

    def upload(self):
        logger.info('uploading...')
        if os.path.exists(self.local_file):
            self.s3.Bucket(self.bucket_name).upload_file(self.local_file, self.s3_file)
        
