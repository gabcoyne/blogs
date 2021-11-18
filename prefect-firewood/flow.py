from typing import List
import requests
import prefect
from prefect import task, Flow
from prefect.tasks.secrets import PrefectSecret
from prefect.client import Secret
from datetime import timedelta
from prefect.storage import GitHub
from prefect.schedules import CronSchedule


@task(name="Find Downed Trees", max_retries=3, retry_delay=timedelta(minutes=1))
def find_trees():
    url = "https://data.cityofchicago.org/resource/mab8-y9h3.json"

    payload = {"status": "Open", "ward": "45"}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


@task(name="Extract Valuable Data")
def transform(response: list):
    return [(i["street_address"], i["creation_date"]) for i in response]


@task(name="Send Text Message", max_retries=3, retry_delay=timedelta(minutes=1))
def send_text(sms_number: str, data: List[tuple]):

    addresses = "".join(
        ["".join(f"\n{created}\n near {address}") for address, created in data]
    )
    message = f"Downed trees reported at: {addresses}"
    resp = requests.post(
        "https://textbelt.com/text",
        {
            "phone": sms_number,
            "message": message,
            "key": Secret("SMS_API_KEY").get(),
        },
    )


with Flow(
    "Free Firewood",
    storage=GitHub(
        repo="gabcoyne/blogs",
        path="prefect-firewood/flow.py",
        access_token_secret="GITHUB_PAT",
    ),
    schedule=CronSchedule(cron="0 7-18 * * *"),
) as flow:

    trees = find_trees()
    transformed_data = transform(trees)
    sms_number = PrefectSecret("SMS_PHONE_NUMBER")
    sent_text = send_text(sms_number=sms_number, data=transformed_data)


if __name__ == "__main__":
    flow.run(run_on_schedule=False)
