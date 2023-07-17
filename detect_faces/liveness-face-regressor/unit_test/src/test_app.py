# Add the path to the src directory to the Python path
import sys
import os

sys.path.insert(0, os.path.abspath('..'))

import unittest
from unittest.mock import patch
import json
import importlib
face_server = importlib.import_module("face-server")


class TestRegressFace(unittest.TestCase):
    
    def setUp(self):
        self.app = face_server.app.test_client()
        self.app.testing = True

    @patch('src.model.regression.Regressor.detect')
    def test_regress_face_with_images(self, detect):
        # Test if the route `/regress-face` is able to handle a POST request with a 
        # list of images in the request payload and return a 200 status code with 
        # the list of image responses in the body.
        
        detect.return_value= {"bboxes": [[9,10,11,12], [9,10,11,12]], "keypoints": [[9,10,11,12], [9,10,11,12]], "keypoints_478": [[9,10,11,12], [9,10,11,12]], "yaw": [9,10,11,12], "pitch": [9,10,11,12], "scores": [9,10,11,12], "has_obstruction": [9,10,11,12], "correctly_framed": [9,10,11,12]}
        images = [open("unit_test/src/img.png", 'rb'), open("unit_test/src/img.png", 'rb')]
        data = {}
        data['images'] = images

        headers = {'Content-Type': 'multipart/form-data'}

        # Send a POST request to the route `/regress-face` with the request payload
        response = self.app.post('/regress-face', headers=headers, data=data)

        # Check if the status code of the response is 200
        self.assertEqual(response.status_code, 200)

        # Check if the response body is a list of image responses
        self.assertAlmostEqual(json.loads(response.get_data()), detect.return_value)

    def test_regress_face_without_images(self):
        # Test if the route `/regress-face` returns a 422 status code with an error message in the body if the request payload does not contain any images.
        # Construct the request payload without any images
        data = {}
        data['images'] = []
        # Send a POST request to the route `/regress-face` with the request payload
        response = self.app.post('/regress-face', data=data, content_type='multipart/form-data')

        # Check if the status code of the response is 422
        self.assertEqual(response.status_code, 422)
        # Check if the response body contains an error message
        self.assertIn('err', json.loads(response.get_data()))

    def test_healthcheck(self):
        # Test if the route `/` is able to handle a
        # Send a GET request to the route /
        response = self.app.get('/')

        # Check if the status code of the response is 200
        self.assertEqual(response.status_code, 200)

        # Check if the response body is "healthy!"
        self.assertEqual(response.get_data(), b'healthy!')

    def test_request_id(self):
        # Test if the `request_id` field is present in the response if the request header contains a `Param-Request-Id` field.
        # Construct the request payload with a list of images
        data = {}
        data['images'] = [open('unit_test/src/img.png', 'rb'), open('unit_test/src/img.png', 'rb')]

        # Set the `Param-Request-Id` field in the request header
        headers = {'Param-Request-Id': '123456'}

        # Send a POST request to the route `/regress-face` with the request payload and the request header
        response = self.app.post('/regress-face', data=data, headers=headers, content_type='multipart/form-data')

        # Check if the `request_id` field is present in the response
        self.assertIn('request_id', json.loads(response.get_data())[0] )

    def test_errs(self):
        # Test if the `errs` field is present in the response if there are errors that occurred while processing the request.
        # Construct the request payload with a list of images
        data = {}
        data['images'] = [open('unit_test/src/img.png', 'rb'), open('unit_test/src/img.png', 'rb')]

        # Send a POST request to the route `/regress-face` with the request payload
        response = self.app.post('/regress-face', data=data, content_type='multipart/form-data')

        # Check if the `errs` field is present in the response
        self.assertIn('errs', json.loads(response.get_data()))

if __name__ == 'main':
    unittest.main() 