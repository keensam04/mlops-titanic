import argparse
import os

import boto3

from model.config import MODEL_FILES_LOCATION
from model.flask_predict_app import create_app

parser = argparse.ArgumentParser()
parser.add_argument("--bucket", help="s3 bucket to use", default=None)
parser.add_argument(
    "--model-path", help="path to dump the training output", default=None
)


def load_model_config():
    args = vars(parser.parse_args())
    bucket = args["bucket"]
    model_path = args["model_path"]
    if bucket and model_path:
        print("Config load started!")
        local_path = f"{MODEL_FILES_LOCATION}/model.json"
        localstack_url = os.getenv("LOCALSTACK_URI")
        s3 = boto3.client("s3", endpoint_url=localstack_url)
        s3.download_file(bucket, model_path, local_path)
        print(f"Model config loaded from s3://{bucket}/{model_path} to {local_path}")
        print("Config load done!")


if __name__ == "__main__":
    load_model_config()
    app = create_app()
    app.run(host="0.0.0.0", port=8090)
