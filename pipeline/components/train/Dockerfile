FROM python:3.10-slim-bullseye

ARG LOCALSTACK_URI
ARG MLFLOW_TRACKING_URI

WORKDIR /opt/component
ENV PYTHONPATH=. LOCALSTACK_URI=$LOCALSTACK_URI MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI

COPY pipeline/components/train/* .
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev libgomp1 -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install -q --no-cache-dir -r requirements.txt
RUN useradd -u 1199 non-root
RUN chown -R non-root:non-root /opt/component
RUN chmod 755 /opt/component
USER non-root

ENTRYPOINT ["python", "train.py"]
