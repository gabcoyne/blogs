import prefect
from prefect import Flow, Parameter, task
from prefect.tasks.aws.batch import BatchSubmit
from prefect.tasks.aws.client_waiter import AWSClientWait
from prefect.storage import S3
from prefect.run_configs import ECSRun
from prefect.tasks.secrets import PrefectSecret
from prefect.utilities.aws import get_boto_client
from prefect.backend.artifacts import create_link_artifact

FLOW_NAME = "tcf-delta-load"  # name of your flow in cloud UI
PROJECT_NAME = (
    "tokenized-channel-fullfillment"  # project that flows/runs are attached to
)
STORAGE = S3(
    bucket="sgmt-prefect-dev-flows", secrets=["AWS_CREDENTIALS"]
)  # bucket where flows are stored. Updates to this require you to run locally.


batch_waiter = AWSClientWait(
    client="batch",
    waiter_name="JobComplete",
)


batchjob = BatchSubmit(
    job_definition="tcf-delta-load",
    job_queue="tcf-tokenization",
)


@task
def get_log_stream_name(job_id):
    # let's attempt to get the log stream name
    batch_client = get_boto_client("batch")
    response = batch_client.describe_jobs(jobs=[job_id])
    logStreamName = response["jobs"][0]["attempts"][0]["logStreamName"]
    if logStreamName:
        create_link_artifact(logStreamName)


with Flow(FLOW_NAME, storage=STORAGE) as flow:
    logger = prefect.context.get("logger")
    tcf_access_key = PrefectSecret("TCF_PROCESSOR_ACCESS_KEY")
    tcf_secret = PrefectSecret("TCF_PROCESSOR_SECRET_ACCESS_KEY")
    partner_id = Parameter("partner_id", default="0")
    s3_key = Parameter("key", default="no-key-given")
    env_id = Parameter("env", default="")
    batch_job = batchjob(
        job_name=f"tcf-delta-load-{partner_id}",
        batch_kwargs={
            "parameters": {
                "partner_id": partner_id,
                "key": s3_key,
                "tcf_access_key": tcf_access_key,
                "tcf_secret": tcf_secret,
            },
            "containerOverrides": {
                "environment": [{"name": "ENVIRONMENT", "value": env_id}]
            },
        },
    )

    batch_waiter = batch_waiter(
        waiter_kwargs={
            "jobs": [batch_job],
            "WaiterConfig": {"Delay": 10, "MaxAttempts": 10},
        }
    )
    # log stream name not available until job is running
    # wait_for_batch_job_state(jobid, state="JobRunning", delay=1, max_attempts=60)
    # get_log_stream_name(jobid)
    # wait for job to be complete
    # wait_for_batch_job_state(jobid)

if __name__ == "__main__":
    flow.run_config = ECSRun(image="prefecthq/prefect:latest-python3.8")

    flow.register(project_name=PROJECT_NAME, labels=["dev"])
