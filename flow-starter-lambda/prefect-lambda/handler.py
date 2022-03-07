import json
import logging
import os
import typing
from datetime import datetime

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


def get_memory_required(s3_key: str, s3_bucket: str):
    default_memory_required = 100000
    try:
        memory_required = 0
        bucket = s3_key["loc"].replace("s3://", "").split("/")[0]
        key = s3_key["loc"].replace(f"s3://{bucket}/", "")
        print(s3_bucket, key)
        for key in s3_client.list_objects(Bucket=s3_bucket, Prefix=key)["Contents"]:
            memory_required = memory_required + key["Size"]
        return memory_required
    except Exception as ex:
        print(ex)
        return default_memory_required


def run(event, context):
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    logger.info(f"Received message via object {s3_key} in bucket {s3_bucket}")

    prefect_response = trigger_flow_run(
        bucket_name=s3_bucket,
        s3_key=s3_key,
        memory_request=get_memory_required(s3_key=s3_key, s3_bucket=s3_bucket),
    )

    logger.info(f"Flow Run ID: {prefect_response}")
    return {"success": True}
