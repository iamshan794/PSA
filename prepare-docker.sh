#!/bin/bash 

set -e  

image_name="${1:-google_adk}"
image_tag="latest"

#Skip image build if matching image name and tag exists
is_image=$(docker images -q "${image_name:image_tag}") 

if [[ -z $is_image ]];then 
    echo "Building image from dockerfile"
    docker buildx build . -t "${image_name}:${image_tag}"
    echo "Build successful."
fi 

echo "Starting container"
docker compose up -d 