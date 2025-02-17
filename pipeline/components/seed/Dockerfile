FROM python:3.10-slim-bullseye

# passed to the Docker build process using the --build-arg flag
ARG AWS_REGION
ARG LOCALSTACK_URI

WORKDIR /opt/component
ENV PYTHONPATH=. AWS_REGION=$AWS_REGION LOCALSTACK_URI=$LOCALSTACK_URI

COPY pipeline/components/seed/* .
COPY data ./data
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install -q --no-cache-dir -r requirements.txt
RUN useradd -u 1199 non-root
USER non-root

ENTRYPOINT ["python", "seed.py"]
