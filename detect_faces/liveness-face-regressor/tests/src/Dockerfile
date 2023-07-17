FROM python:3.8.5
MAINTAINER Igor Marques
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt update -y && apt install ffmpeg libsm6 libxext6 -y
COPY . .
CMD pytest test_face_regressor.py -s -v --maxfail=50 --log-cli-level=INFO --import-mode importlib
