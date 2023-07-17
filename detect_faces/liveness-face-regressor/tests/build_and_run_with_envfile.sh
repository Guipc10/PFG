cd docker
docker-compose --env-file ~/dir_ssh/a.env -f docker-compose.yml build
docker-compose --env-file ~/dir_ssh/a.env -f docker-compose.yml up --exit-code-from face_regressor_test
