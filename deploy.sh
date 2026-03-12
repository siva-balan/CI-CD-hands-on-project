#!/bin/bash
container=fix_log_analyzer
image=fix_log_analyzer

echo "Stopping container: $container"
docker stop $container 2>/dev/null
docker rm $container 2>/dev/null

echo "Staring new  container $container with image $image"
docker run -d -p 8090:5000 --name $container $image
