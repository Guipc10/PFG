export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1 
docker-compose   -f compose.yml up --remove-orphans

