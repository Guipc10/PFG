FROM python:3.8.2-slim

RUN apt update -y && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y npm python3-dev protobuf-compiler  python3-pip cmake

RUN npm install -g @bazel/bazelisk

COPY liveness-face-regressor/mediapipe /app/mediapipe
WORKDIR /app/mediapipe/ 
RUN bash setup_opencv.sh && pip3 install -r requirements.txt && python3 setup.py gen_protos && python3 setup.py install --link-opencv && rm -r /app/mediapipe

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN rm /requirements.txt

COPY . /app
WORKDIR /app



CMD python crop_faces.py -d /app/data -o /app/data/cropped_faces