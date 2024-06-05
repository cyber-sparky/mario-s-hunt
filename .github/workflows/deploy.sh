#! /bin/bash

export $(cat .env | xargs)
docker login ghcr.io -u $GITHUB_ACTOR -p $GITHUB_TOKEN

# Stop and remove the existing containers if they exist
docker-compose down

# Pull the latest image
docker-compose pull web

# Start the services
docker-compose up -d

# Clean up the .env file
rm .env
