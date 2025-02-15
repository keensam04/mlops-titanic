import argparse
import os

import boto3
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser()
parser.add_argument("--bucket", help="s3 bucket to use")
parser.add_argument("--param-path", help="s3 path to dump training param file")
parser.add_argument("--train-path", help="s3 path to dump training data")
parser.add_argument("--test-path", help="s3 path to dump test data")


def seed(bucket: str, param_path: str, train_path: str, test_path: str):
    localstack_url = os.getenv("LOCALSTACK_URI")
    region = os.getenv("AWS_REGION")
    print(f"endpoint_url={localstack_url} region={region}")
    s3 = boto3.client("s3", endpoint_url=localstack_url)
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "404":
            # bucket does not exist
            s3.create_bucket(
                Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region}
            )
            print("Bucket does not exist; Created Bucket=%s Region=%s", bucket, region)

    s3.put_object(Body=open("data/params.json", "rb"), Bucket=bucket, Key=param_path)
    print(f"Param file dumped to Bucket={bucket} Key={param_path}")
    s3.put_object(
        Body=open("data/titanic/train.csv", "rb"), Bucket=bucket, Key=train_path
    )
    print(f"Train data file dumped to Bucket={bucket} Key={train_path}")
    s3.put_object(
        Body=open("data/titanic/test.csv", "rb"), Bucket=bucket, Key=test_path
    )
    print(f"Test data file dumped to Bucket={bucket} Key={test_path}")


def main():
    args = vars(parser.parse_args())
    print("Seeding started!")
    seed(**args)
    print("Seeding done!")


if __name__ == "__main__":
    main()
