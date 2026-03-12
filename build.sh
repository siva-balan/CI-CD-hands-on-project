#!/bin/bash
Image_name=sivabalansp/fix_log_analyzer:$BUILD_NUMBER
echo "Building Docker image: $Image_name"
docker build -t $Image_name .
docker tag $Image_name sivabalansp/fix_log_analyzer:latest