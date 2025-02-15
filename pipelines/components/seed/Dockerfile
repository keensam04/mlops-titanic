FROM python:3.10-slim-bullseye

ARG AWS_REGION
ARG LOCALSTACK_URI

WORKDIR /opt/component
ENV PYTHONPATH .
ENV AWS_REGION $AWS_REGION
ENV LOCALSTACK_URI $LOCALSTACK_URI

COPY pipelines/components/seed/seed.py .
COPY pipelines/components/seed/requirements.txt .
COPY data ./data
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev -y
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -u 1199 non-root
USER non-root

ENTRYPOINT ["python", "seed.py"]
