FROM python:3.10-slim-bullseye

ARG LOCALSTACK_URI

WORKDIR /opt/component
ENV PYTHONPATH=. LOCALSTACK_URI=$LOCALSTACK_URI

COPY pipeline/components/pre-processing/* .
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install -q --no-cache-dir -r requirements.txt
RUN useradd -u 1199 non-root
USER non-root

ENTRYPOINT ["python", "pre_processing.py"]
