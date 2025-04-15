#!/bin/bash
TAG=$(git describe --tag --always)
echo "Building with tag: ${TAG}"
COMPOSE_BAKE=true
echo "Building for amd64"
docker buildx build --platform linux/amd64 -t thet4/civitaikido:${TAG}-amd64 --load .
echo "Building for arm64"
docker buildx build --platform linux/arm64 -t thet4/civitaikido:${TAG}-arm64 --load .
