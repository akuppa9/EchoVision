#!/bin/bash

IMAGE_NAME="echovision"
CONTAINER_NAME="echovision_container"
HOST_DIR="/home/eashan/workspace"
CONTAINER_SRC_DIR="/workspace"

docker rm $CONTAINER_NAME

docker run -it \
    --name "$CONTAINER_NAME" \
    --network host \
    --privileged \
    -v "$HOST_DIR":"$CONTAINER_SRC_DIR" \
    "$IMAGE_NAME" \
    /workspace/echovision/host/main.py