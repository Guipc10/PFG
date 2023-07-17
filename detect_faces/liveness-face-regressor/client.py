import asyncio
import uuid
import argparse
import importlib

# Getting the client to do the requests.
comm_client = importlib.import_module("tests.src.liveness-tests-s3-client.s3-client.comm_client")
cc = comm_client.CommClient()

async def get_images_roi(test_zip_path):
    '''
        Make the request to the face regressor.
    '''
    loop = asyncio.get_event_loop()
    cc.regressor_comm.set_event_loop(loop)

    request_id = uuid.uuid4().hex
    file = open(test_zip_path, 'rb').read()
    images = await cc.parse_zip_file(file)
    
    prediction = await cc.get_images_roi(images, request_id)
    json_test = dict(imgs_roi = prediction.bboxes)

    return json_test

async def main():
    '''
        Do a request to the action recognition. -f files is the path to a zip file.
    '''
    
    parser = argparse.ArgumentParser(description='Test Client for face regressor detection')
    parser.add_argument('-f', '--files')
    args = parser.parse_args()

    path = args.files
    if path[-1] == "/":
        path = path[:-1]

    # Making the requests
    face_regressor_prediction = await get_images_roi(path)
    print(face_regressor_prediction)


if __name__ == "__main__":
    asyncio.run(main())