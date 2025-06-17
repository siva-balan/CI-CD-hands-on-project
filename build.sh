#!/bin/bash
Image_name=website
echo "Building Docker image: $Image_name"
docker build -t $Image_name .
