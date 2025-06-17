#!/bin/bash
container=website
image=website

echo "Stopping container: $container"
docker stop $container 2>/dev/null
docker rm $container 2>/dev/null

echo "Staring new  container $container with image $image"
docker run -d -p 8090:80 --name $container $image
