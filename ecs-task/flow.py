from prefect import Flow, task, Parameter
from prefect.tasks.aws.batch import BatchSubmit
from prefect.tasks.aws.client_waiter import AWSClientWait
from prefect.client import Secret
from prefect.backend.kv_store import get_key_value


batch_submit = BatchSubmit()

batch_observer = AWSClientWait(
    client="batch",
    waiter_name="JobComplete",
)

with Flow("batch-jobs") as flow:
    cowsay = Parameter(name="cowsay", default="segmint")
    batch_job_cowsay = batch_submit(
        job_name="whalesay-demo",
        job_definition="whalesay",
        job_queue="whalesay-queue",
        batch_kwargs={
            "containerOverrides": {
                "environment": [{"name": "COMMAND", "value": cowsay}],
                "vcpus": 1,
                "memory": 128,
            },
        },
        task_args=dict(log_stdout=True),
    )
    observe_jobs = batch_observer(
        waiter_kwargs={
            "jobs": [batch_job_cowsay],
            "WaiterConfig": {"Delay": 10, "MaxAttempts": 10},
        }
    )

if __name__ == "__main__":
    flow.run()
