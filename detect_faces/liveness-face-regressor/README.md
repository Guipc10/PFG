This module does a face detection, face landmarks extraction, pose estimation and obstruction checking in all the given video frames. The sections below explains how this is made, its API's routes, most important envs and also its DevOps pipeline.

## Inference models

Eventhough there are three inference models (face detection, landmarks extaction and hand detection), none of them was trained by us, they are all from Mediapipe and publicly available.

### Face detection and landmarks extraction

When a sequence of frames arrive at the API, the first thing that is done is the face detection followed by the extraction of 478 landmarks, this is made using [Mediapipe's Facemesh](https://google.github.io/mediapipe/solutions/face_mesh.html).

The 478 landmarks are then used to get the bbox coordinates of the detected face, are converted to the 68 points format (but the 478 are also returned by the api) and used to estimate the pose of the face.

This is currently the time bottleneck of this module and liveness as a whole, runs on CPU.

### Pose estimation

The pose of the face (yaw and pitch) is estimated by checking how some lines of the face change during the movement of the head.

The idea came from [this article](https://edusj.mosuljournals.com/article_169071_92fb8de5c14f5011621ad74429f9ba1b.pdf).


### Obstruction checking

Next is made the palm obstruction checking, this is necessary because sometimes people obstruct their faces with their hands, what may influence the behavior of the movement detection.

The palms are detected using [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html), that infers 21 3D landmarks from just a single frame. Just the ones necessary for getting the bounding box of the hands are used, these boxes are then compared with the face bounding boxes, if there is an intersecction then it's considered an obstruction and the corresponding frame is not used in the rest of the Liveness pipeline.

This module runs on CPU.

## API's routes, inputs and outputs

There are two routes for this module's API:

- "/"
    Method: GET
    Summary: Healthcheck

- "/regress-face"
    Method: POST
    Summary: Given a sequence of frames belonging to a video, returns for each frame: original image, face cropped image, face bounding box, scores for the bboxes, facial landmarks in the 68 and 478 points format, yaw, pitch and whether it's obstructed by a hand or not
    Input:

        {
            "images" : List[Bytes],
            "request_id" : string -> the ID of the request
        }

    Output:

        {
            "images_cropped": List[bytes] -> images cropped around the face region
            "images_n": List[bytes] -> original images
            keypoints: List[List[tuple]] -> detected keypoints in the 68 points format
            keypoints_478: List[List[tuple]] -> detected keypoints in the 478 points format
            yaw_lst: List[float] -> estimated yaw list
            pitch_lst: List[float] -> estimated pitch list
            bboxes: List[List[tuple]] -> detected bbox coordinates in the (xmin,ymin,xmax,ymax) format
            scores: List[float] -> confidence scores of the face detections
            has_obstruction: List[bool] -> whether the frames have a hand obstructing the face or not
        }

## ENV Variables

The most important envs are:

- PORT -> Port that the api will listen to, default: 4013
- N_WORKERS -> Number of workers, default: 1
- KEEPALIVE -> Number of seconds to wait for requests on a Keep-Alive connection, default: 300
- TIMEOUT -> Workers silent for more than this many seconds are killed and restarted, default: 300
- LOG_LEVEL -> Log level, default: info

## DevOps

This module has a pre-commit config file to make commits go through a first check before submission to code review. Therefore, first of all make sure you have pre-commit installed with:
'pip install pre-commit'

Then go inside the cloned repository that has the .pre-commit-config.yaml in it and run:
'pre-commit install'

Now pre-commit will run automatically on git commit!

To make your code changes available in production you have to do the following steps:

1. First make sure you made the changes in a separated branch;
2. Merge the branch into branch master, add someone as a reviewer;
3. Merge the branch master into branch dev;
4. Check if the tests stage in the CI/CD pipeline was successfull;
5. If your change added too much complexity to the code, also do a load test in dev(you can do it using Locust);
6. If all the tests were successfull, do a merge into branch prod, add someone as a reviewer;
