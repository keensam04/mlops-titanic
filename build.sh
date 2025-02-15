#!/bin/bash

docker-compose up -d

VERSION=1.0
LOCALSTACK_URI=http://host.docker.internal:4566
MLFLOW_TRACKING_URI=http://host.docker.internal:5000
AWS_REGION=us-west-2


docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} --build-arg AWS_REGION=${AWS_REGION} -t mlops-titanic/pipeline/components/seed:${VERSION} -f pipeline/components/seed/Dockerfile .
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} -t mlops-titanic/pipeline/components/preprocessing:${VERSION} -f pipeline/components/pre-processing/Dockerfile .
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} --build-arg MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} -t mlops-titanic/pipeline/components/train:${VERSION} -f pipeline/components/train/Dockerfile .
docker build --build-arg LOCALSTACK_URI=${LOCALSTACK_URI} --build-arg MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} -t mlops-titanic/inference:${VERSION} .

dsl-compile --py pipeline/pipeline.py --out pipeline.yaml