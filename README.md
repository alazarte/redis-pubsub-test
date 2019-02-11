# IRC like using Redis Pub Sub

## Description

This is a small project to test out Redis PubSub capabilities using Python, in 
Docker images.

## Deployment

1. Check `dest/` folder for zip file.
2. Unzip and run `make build`, it should create an image called `chat`
3. Run `make redis` to start redis
4. Run `make run` to start up the application

## Usage

The application shows first a help message with the available commands. Then 
prompts for a username ans channel to join. Channels are created when choosing 
its name, if the name is not known, then the client is joined to a new channel 
with no other clients listening to it. Once in a channel, client can type 
messages and commands. Similar to others IRC, the commands in this chat also 
start with '/'.
