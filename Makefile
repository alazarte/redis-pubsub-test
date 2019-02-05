all: build chat

build:
	docker build -t python-redis .

redis:
	docker run --rm -ti --name redis-service -p 6793 -d redis

chat:
	docker run --rm -ti --link redis-service python-redis
