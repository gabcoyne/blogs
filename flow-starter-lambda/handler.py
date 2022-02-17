import json
import logging
import os
import typing
from datetime import datetime
from botocore.errorfactory import ClientError
import boto3
import prefect
from prefect.run_configs.kubernetes import KubernetesRun

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
ssm_client = boto3.client("ssm", "us-east-1")


def decrypt_parameter(parameter_name: str):
    parameter = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    return parameter["Parameter"]["Value"]


PREFECT_AUTH_TOKEN = decrypt_parameter(f"/{os.getenv('STAGE')}/prefect/token")
PREFECT_VERSION_GROUP_ID = decrypt_parameter(
    f"/{os.getenv('STAGE')}/prefect/my_important_flow/version_group_id"
)
prefect_client = prefect.Client(api_key=PREFECT_AUTH_TOKEN)


def trigger_flow_run(
    bucket_name: str,
    s3_key: list,
    memory_request: int,
) -> dict:
    return prefect_client.create_flow_run(
        run_name=f"{s3_key.split('/')[-1]} Processing Run",
        version_group_id=PREFECT_VERSION_GROUP_ID,
        parameters=dict(
            bucket_name=bucket_name,
            s3_key=s3_key,
        ),
        run_config=KubernetesRun(memory_request=memory_request),
    )


def checkfiles(bucket_name: str, lines: list):
    for hash, path in lines:
        prefix = "novogene/X401SC21083527-Z01-F001"
        s3 = boto3.client("s3")
        key = f"{prefix}/{path}"
        try:
            s3.head_object(Bucket=bucket_name, Key=key)
            print("Found file")
        except ClientError:
            raise ValueError(f"File {key} not found")
    return True


def run(event, context):
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    logger.info(f"Received message via object {s3_key} in bucket {s3_bucket}")

    prefect_response = trigger_flow_run(
        # Assorted parameters for pre-processing
    )

    logger.info(f"Flow Run ID: {prefect_response}")
    return {"success": True}
