from datetime import timedelta
from prefect import Flow, task, Parameter
from prefect.tasks.aws.batch import BatchSubmit
from prefect.tasks.aws.client_waiter import AWSClientWait
from prefect.client import Secret
from prefect.backend.kv_store import get_key_value
from prefect.utilities.aws import get_boto_client
from prefect.backend.artifacts import create_link_artifact
import prefect
import json
import random

batch_submit = BatchSubmit()


@task
def batch_run_name(partner_id: str):
    return f"{partner_id}_{prefect.context.flow_run_name}"


batch_observer = AWSClientWait(client="batch")


@task(max_retries=3, retry_delay=timedelta(seconds=30))
def get_log_stream_name(job_id):
    # let's attempt to get the log stream name
    batch_client = get_boto_client("batch")
    response = batch_client.describe_jobs(jobs=[job_id])
    with open("out_response.json", "w") as j:
        json.dump(response, j)
    logStreamName = response["jobs"][0]["attempts"][0]["container"]["logStreamName"]
    if logStreamName:
        create_link_artifact(
            f"https://console.aws.amazon.com/cloudwatch/home?#logsV2:log-groups/{logStreamName}"
        )
        print(f"Found logs at {logStreamName}")


@task
def print_context():
    print(prefect.context.__dict__)


with Flow("batch-jobs") as flow:
    phrase = Parameter("phrase", default="0")

    batch_job_name = batch_run_name(phrase)
    batch_job_cowsay = batch_submit(
        job_name=batch_job_name,
        job_definition="whalesay",
        job_queue="whalesay-queue",
        batch_kwargs={
            "containerOverrides": {
                "vcpus": 1,
                "memory": 128,
            },
            "parameters": {"phrase": phrase},
        },
        task_args=dict(log_stdout=True),
    )
    complete_job = batch_observer(
        task_args=dict(name="Running Job Waiter"),
        waiter_name="JobComplete",
        waiter_kwargs={
            "jobs": [batch_job_cowsay],
            "WaiterConfig": {"Delay": 10, "MaxAttempts": 10},
        },
    )
    log_artifact_waiter = batch_observer(
        task_args=dict(trigger=prefect.triggers.always_run, name="Running Job Waiter"),
        waiter_name="JobRunning",
        waiter_kwargs={
            "jobs": [batch_job_cowsay],
            "WaiterConfig": {"Delay": 10, "MaxAttempts": 10},
        },
    )

    log_artifact = get_log_stream_name(
        batch_job_cowsay, upstream_tasks=[log_artifact_waiter]
    )

if __name__ == "__main__":
    flow.run()
