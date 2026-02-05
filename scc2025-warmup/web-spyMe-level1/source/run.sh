#!/bin/bash

# Script to build and run the web_spyMe_level1 containers with cache

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down -v

# Build and start the containers with BuildKit enabled
echo "Building containers with cache..."
DOCKER_BUILDKIT=1 docker-compose build

echo "Starting containers..."
docker-compose up -d

echo "Containers are now running!"
echo "Web service is available at: http://localhost:3000"
echo "Admin bot service is available at: http://localhost:3001"

echo "To view logs, run: docker-compose logs -f"
echo "To stop containers, run: docker-compose down" 