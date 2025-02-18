#!/bin/bash

VERSION=1.0
LOCALSTACK_URI=http://host.docker.internal:4566
MLFLOW_TRACKING_URI=http://host.docker.internal:5000
AWS_REGION=us-west-2

echo "Building Seed Component"
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} --build-arg AWS_REGION=${AWS_REGION} -t mlops-titanic/pipeline/components/seed:${VERSION} -f pipeline/components/seed/Dockerfile .

echo "Building Preprocessing Component"
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} -t mlops-titanic/pipeline/components/preprocessing:${VERSION} -f pipeline/components/pre-processing/Dockerfile .

echo "Building Train Component"
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} --build-arg MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} -t mlops-titanic/pipeline/components/train:${VERSION} -f pipeline/components/train/Dockerfile .

echo "Building Inference Container"
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} --build-arg MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} -t mlops-titanic/inference:${VERSION} .

echo "Generating manifest"
dsl-compile --py pipeline/pipeline.py --out pipeline.yaml
echo "Pipeline manifest generated"