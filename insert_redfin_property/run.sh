#!/bin/sh

sudo docker run \
    -e FOLDER_NAME=$1 \
    -e FILE_NAME=$2 \
    --mount type=bind,source=$(pwd),target=/app \
    --name insert-redfin-property-anthony anthony/insert-redfin-property:latest
