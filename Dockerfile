FROM python:3.10-slim-bullseye

ARG LOCALSTACK_URI
ARG MLFLOW_TRACKING_URI

WORKDIR /app
ENV PYTHONPATH=. LOCALSTACK_URI=$LOCALSTACK_URI MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI

COPY model ./model
COPY requirements.txt .
COPY server.py .
COPY pipeline/components/train/ensemble_model.py .
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev libgomp1 -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN useradd -u 1199 non-root
RUN install -d -m 0755 -o non-root -g non-root /var/beacon /opt/ml/model
RUN pip install -q --no-cache-dir -r requirements.txt

USER non-root

ENTRYPOINT ["python", "server.py"]
