FROM python:3.10-slim-bullseye

ARG LOCALSTACK_URI

WORKDIR /opt/component
ENV PYTHONPATH .
ENV LOCALSTACK_URI $LOCALSTACK_URI

COPY pipeline/components/pre-processing/pre_processing.py .
COPY pipeline/components/pre-processing/requirements.txt .
COPY .aws /home/non-root/.aws

RUN apt update
RUN apt install libtirpc-dev -y
RUN apt install libgnutls28-dev -y
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -u 1199 non-root
USER non-root

ENTRYPOINT ["python", "pre_processing.py"]
