FROM python:3.10-slim-bullseye

ARG LOCALSTACK_URI
ARG MLFLOW_TRACKING_URI

WORKDIR /opt/component
ENV PYTHONPATH .
ENV LOCALSTACK_URI $LOCALSTACK_URI
ENV MLFLOW_TRACKING_URI $MLFLOW_TRACKING_URI

COPY pipeline/components/train/train.py .
COPY pipeline/components/train/ensemble_model.py .
COPY pipeline/components/train/plot_funcs.py .
COPY pipeline/components/train/utils.py .
COPY pipeline/components/train/requirements.txt .
COPY .aws /home/non-root/.aws

RUN apt update && apt install libtirpc-dev libgnutls28-dev libgomp1 -y
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -u 1199 non-root
RUN chown -R non-root:non-root /opt/component
RUN chmod 755 /opt/component
USER non-root

ENTRYPOINT ["python", "train.py"]
