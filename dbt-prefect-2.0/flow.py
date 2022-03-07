from datetime import timedelta
from prefect import Flow, storage, task, Parameter
import shutil
import prefect
from prefect.client import Secret
from prefect.run_configs.kubernetes import KubernetesRun
import requests
from prefect.tasks.dbt.dbt import DbtShellTask
import os
from prefect.schedules import clocks, Schedule
from prefect.storage.gitlab import GitLab
from prefect.tasks.control_flow.case import case
from prefect.backend.kv_store import get_key_value


@task(name="Clone repo")
def clone_repo(repo_name):

    shutil.rmtree(repo_name, ignore_errors=True)
    token = Secret("GIT_ACCESS_TOKEN").get()
    dbt_repo = requests.get(
        "REPO_URL",
        verify=False,
        stream=True,
        headers={"PRIVATE-TOKEN": token},
    )
    with open("repo.tar.gz", "wb") as f:
        f.write(dbt_repo.raw.read())
    shutil.unpack_archive(
        "repo.tar.gz",
        format="gztar",
    )
    repo_path = list(
        filter(lambda x: os.path.isdir(x) and x.startswith(repo_name), os.listdir())
    )[0]
    os.rename(repo_path, repo_name)


@task(trigger="all_finished")
def output_print(output):
    logger = prefect.context.get("logger")
    for o in output:
        logger.info(o)


dbt = DbtShellTask(
    return_all=True,
    profile_name="GCoyne_dbt_snowflake",
    environment=get_key_value("DBT_ENV"),
    overwrite_profiles=True,
    profiles_dir=os.getcwd(),
    log_stdout=True,
    helper_script="cd dbt/dbt",
    log_stderr=True,
    stream_output=True,
    dbt_kwargs={
        "type": "snowflake",
        "account": Secret("SNOWFLAKE_ACCOUNT").get(),
        "user": Secret("SNOWFLAKE_USER").get(),
        "password": Secret("SNOWFLAKE_PASSWORD").get(),
        "role": Secret("SNOWFLAKE_ROLE").get(),
        "database": Secret("SNOWFLAKE_DATABASE").get(),
        "warehouse": Secret("SNOWFLAKE__WAREHOUSE").get(),
        "schema": Secret("DBT__SCHEMA").get(),
        "threads": 12,
        "client_session_keep_alive": False,
    },
)

hourly = clocks.IntervalClock(
    interval=timedelta(hours=1), parameter_defaults={"run_type": "hourly"}
)
daily = clocks.IntervalClock(
    interval=timedelta(hours=24), parameter_defaults={"run_type": "daily"}
)
schedule = Schedule(clocks=[hourly, daily])

storage = GitLab(
    repo="MY_REPO",
    path="prefect-flow/flow.py",
    access_token_secret="GIT_ACCESS_TOKEN",
)

with Flow(
    "GCoyne DBT",
    storage=storage,
    schedule=schedule,
    run_config=KubernetesRun(image="MY_IMAGE"),
) as flow:

    clock_type = Parameter("run_type", default=None, required=False)
    dbt_repo = clone_repo("dbt")
    deps = dbt(
        command="dbt deps",
        task_args={"name": "DBT: Dependencies"},
        upstream_tasks=[dbt_repo],
    )
    debug = dbt(
        command="dbt debug",
        task_args={"name": "DBT: debug"},
        upstream_tasks=[deps],
    )

    source_snapshop = dbt(
        command="dbt source freshness",
        task_args={"name": "DBT: Source snapshot"},
        upstream_tasks=[deps, debug],
    )
    run_hourly = dbt(
        command="dbt run --model tag:hourly",
        task_args={"name": "DBT: Run Hourly"},
        upstream_tasks=[source_snapshop, debug],
    )
    with case(clock_type, "daily"):
        run_daily = dbt(
            command="dbt run --exclude tag:hourly",
            task_args={"name": "DBT: Run Dailies"},
            upstream_tasks=[source_snapshop, debug],
        )

if __name__ == "__main__":
    flow.run(run_on_schedule=False, parameters={"run_type": "daily"})
