.PHONY: build up down logs restart deploy

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

deploy:
	git pull origin main
	docker compose up --build -d
