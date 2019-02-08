all: build run

build:
	docker build -t chat .

redis:
	docker run --rm -ti --name redis-service -p 6793 -d redis

run:
	docker run --rm -ti --link redis-service chat

sonar:
	docker run -d --name sonarqube -p 9000:9000 sonarqube
