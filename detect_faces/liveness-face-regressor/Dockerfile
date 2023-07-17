FROM python:3.8.2-slim

RUN apt update -y && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y npm python3-dev protobuf-compiler  python3-pip cmake

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN rm /requirements.txt

RUN npm install -g @bazel/bazelisk

COPY mediapipe/ /app/mediapipe
WORKDIR /app/mediapipe
RUN bash setup_opencv.sh && pip3 install -r requirements.txt && python3 setup.py gen_protos && python3 setup.py install --link-opencv && rm -r /app/mediapipe

COPY src/ /app/src
COPY face-server.py /app/face-server.py

ENV PWD="/app"
ENV PORT 4011
EXPOSE 4011
ENV N_WORKERS 4
ENV KEEPALIVE 300
ENV LOG_JSON True
ENV LOG_LEVEL "INFO"
ENV TIMEOUT 300
WORKDIR /app
CMD gunicorn face-server:app \
    -w ${N_WORKERS} \
    -b 0.0.0.0:${PORT} \
    --log-level ${LOG_LEVEL} \
    --timeout ${TIMEOUT} \
    --keep-alive ${KEEPALIVE}
