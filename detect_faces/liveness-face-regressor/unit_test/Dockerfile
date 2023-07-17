FROM python:3.8.2-slim

RUN apt update -y && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y npm python3-dev protobuf-compiler  python3-pip cmake

COPY unit_test/requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN rm /requirements.txt

RUN npm install -g @bazel/bazelisk

COPY mediapipe/ /app/mediapipe
WORKDIR /app/mediapipe
RUN bash setup_opencv.sh && pip3 install -r requirements.txt && python3 setup.py gen_protos && python3 setup.py install --link-opencv && rm -r /app/mediapipe

COPY src/ /app/src
COPY face-server.py /app/face-server.py
COPY unit_test/     /app/unit_test

WORKDIR /app
RUN python3 -m pytest -vv unit_test/src --cov-config=unit_test/.coveragerc --cov=.