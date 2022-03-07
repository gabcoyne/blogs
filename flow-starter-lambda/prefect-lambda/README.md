# Easy Event-driven workflows with AWS Lambda V2 featuring Serverless Framework
## Prefect makes it easy to do hard work.

Outline
- Introduction
- Lambda + Prefect
- Serverless Framework
- Closing


### Introduction

There are a myriad of reasons that one may wish to trigger a Prefect Flow Run from an event. One of the most common use cases that we have encountered is: A file lands in object storage (S3, GCS, Azure Blob) and will be the input to a Prefect flow.

Chris White wrote an awesome [blog]("https://medium.com/the-prefect-blog/event-driven-workflows-with-aws-lambda-2ef9d8cc8f1a") a few years back about using AWS Lambda to trigger prefect flows through Prefect Cloud GraphQL API. Since then the team have been working hard to [reduce negative engineering](https://medium.com/the-prefect-blog/positive-and-negative-data-engineering-a02cb497583d) and in the process make event driven Flows even easier.

Of this pattern the feature that I find most useful is the ability to pass overrides to the [Run Config]("https://docs.prefect.io/orchestration/flow_config/run_configs.html") - specifically the setting an ECS/Kubernetes overrides to ensure that our work runs on the appropriate infrastructure.

In our example below we have a Lambda that will check for a file size in S3, then use the Run Config to set a memory request, which will ensure that an instance with a sufficient amount of memory schedules the Flow.


### The Lambda

Our lambda is going to use the Prefect client to kick off our Flow. Now we could do all of this through the GraphQL API, and use requests or urrlib, but the Prefect client keeps our code tidy, legible, and easy to modify.

Let's walk through our Lambda function:
- `decrypt_parameter` decrypts secrets from AWS SSM Parameter Store.
- Our `run` function takes an S3 PUT event and extracts Bucket and Key from the payload.
- `get_memory_required` interrogates the S3 API for information about the size of the file that was uploaded.
- `trigger_flow_run` kicks off a Prefect FlowRun with a custom name derived from the S3 key. We pass the file size derived from `get_memory_required` to the KubernetesRun RunConfig in order to set a memory request on the Kubernetes job that will be running our Flow.

A key point here. We are using the `version_group_id` which is:
    The unique unarchived flow within this version group will be scheduled to run. This input can be used as a stable API for running flows which are regularly updated.

This allows us to set our lambda and forget it, triggering the desired flow regardless of new versions.

# Lambda Deployment

Personally, I feel that the AWS native experience of deploying Python lambda functions is a bad time. Whether through the console or through AWS CLI the installing and zipping and dependency management is a chore. There are several tools that reduce the pain of deployment, my favorite is [serverless framework]("serverless.io").

Serverless allows us to define our function in a simple `serverless.yml` file. Further serverless has their own concept of plugins, most relevant to us is the [`serverless-python-requirements`]("https://github.com/UnitedIncome/serverless-python-requirements") plugin, which makes the packaging of python requirements painless. The file is broken up into arrays from top to bottom:

-  `provider` defines platform specific configurations, in our case we have lambda runtime settings, and some IAM role configurations.
-  `functions` defines any number of lambda functions as well as some incredibly useful ancillary options
   - `handler` specifies from which function lambda is going to start our function.
   - `layers` allows us to take advantage of the work that our `serverless-python-requirements` plugin does, and package the python reqs separately from our code, which means that we can still edit code in the lambda IDE.
   -  `events` is one of my favorites, in our example we are essentially subscribing our function to specific events from an s3 bucket.


Putting it all together we run `serverless deploy` and watch as `serverless`:
- Spins up a docker container to package all of the aforementioned python requirements
- Creates cloudformation templates from our yaml file
- Zips up our code and dependencies
- Uploads everything to S3

Once deployed we can test by dropping a file in the specified bucket or triggering through the lambda console.


### Conclusion
The Prefect Client provides a straightforward way to interact with Prefect API's. Kicking off FlowRuns is just a small example of the use ways that users can take advantage of our Cloud API.

Prefect is the new standard for dataflow automation, our ultimate mission is to eliminate negative engineering by ensuring that data professionals can confidently and efficiently automate their data applications with the most user-friendly toolkit around.


Join our [Slack]("https://join.slack.com/t/prefect-community/shared_invite/enQtODQ3MTA2MjI4OTgyLTliYjEyYzljNTc2OThlMDE4YmViYzk3NDU4Y2EzMWZiODM0NmU3NjM0NjIyNWY0MGIxOGQzODMxNDMxYWYyOTE") community for ad-hoc questions
Follow us on [Twitter]("https://twitter.com/PrefectIO") for updates
Visit us on [GitHub]("https://github.com/PrefectHQ/prefect") to open issues and pull requests

