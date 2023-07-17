cd docker
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up --exit-code-from face_regressor_test

#docker build -t img_face_regressor_test -f face_regressor_test.dockerfile .
#docker-compose up
