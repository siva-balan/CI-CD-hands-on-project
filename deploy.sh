#!/bin/bash
container=fix_log_analyzer
Image_name=sivabalansp/fix_log_analyzer:$BUILD_NUMBER

echo "Stopping container: $container"
docker stop $container 2>/dev/null
docker rm $container 2>/dev/null

echo "Staring new  container $container with image $image"
docker run -d -p 8090:5000 --name $container $image
