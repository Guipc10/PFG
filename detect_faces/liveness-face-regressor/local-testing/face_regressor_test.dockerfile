FROM python:3.8.5
MAINTAINER Igor Marques
COPY . .
RUN pip3 install -r requirements.txt
CMD pytest test_face_regressor.py -s -v --maxfail=10
