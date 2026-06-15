DOCKER_COMPOSE_FILE_PROD = docker-compose.yml
DOCKER_COMPOSE_FILE_TEST = docker-compose.test.yml

install:
	poetry install

migrate:
	poetry run alembic revision --autogenerate -m "$(msg)"

upgrade:
	poetry run alembic upgrade head

downgrade:
	poetry run alembic downgrade -1

docker-up:
	docker compose -f $(DOCKER_COMPOSE_FILE_PROD) up -d --build

docker-down:
	docker compose -f $(DOCKER_COMPOSE_FILE_PROD) down

test:
	docker compose -f $(DOCKER_COMPOSE_FILE_TEST) up --build --abort-on-container-exit --exit-code-from test-app
	docker compose -f $(DOCKER_COMPOSE_FILE_TEST) down

lint:
	poetry run ruff check src tests
	poetry run mypy src

format:
	poetry run black --target-version=py314 src tests
	poetry run ruff check --fix src tests
