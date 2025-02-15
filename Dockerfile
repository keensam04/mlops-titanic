FROM python:3.10-slim-bullseye

ARG LOCALSTACK_URI
ARG MLFLOW_TRACKING_URI

WORKDIR /var/beacon
WORKDIR /opt/ml/model
WORKDIR /app
ENV PYTHONPATH .
ENV LOCALSTACK_URI $LOCALSTACK_URI
ENV MLFLOW_TRACKING_URI $MLFLOW_TRACKING_URI

COPY model ./model
COPY requirements.txt .
COPY server.py .
COPY pipeline/components/train/ensemble_model.py .
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev libgomp1 -y
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -u 1199 non-root
RUN chown -R non-root:non-root /opt/ml/model && chmod 755 /opt/ml/model
RUN chown -R non-root:non-root /var/beacon && chmod 755 /var/beacon
USER non-root

ENTRYPOINT ["python", "server.py"]
