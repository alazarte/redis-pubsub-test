all: build run

build:
	docker build -t chat .

redis:
	docker run --rm -ti --name redis-service -p 6793 -d redis

redis-cli:
	docker run -it --link redis-service:redis --rm redis redis-cli -h redis -p 6379

run:
	docker run --rm -ti --link redis-service chat

sonar:
	docker run --rm --name sonarqube -p 9000:9000 -d sonarqube

scanner:
	sonar-scanner -D sonar.projectName=redis-pubsub-test -D sonar.projectKey=redis-pubsub-test -D sonar.sources=chat/

zip:
	zip -r deploy/chat.zip chat/
