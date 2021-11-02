# Canvas Create Flow

## Deployment
To deploy this flow to Prefect Cloud, ensure that your Prefect CLI is authenticated with Prefect Cloud, your local Docker client is running, and that your Docker client is authenticated to ECR. The following command will build a new Docker image, upload the image to ECR, and register the flow with Prefect Cloud:
```
prefect register --project "ElasticSearch Canvas Load" --path canvas_create_flow.py
```

## Secrets
This flow is dependent on the following secret values being present:

- ELASTICSEARCH_USER 
  - *string* 
  - Username used to authenticate with ElasticSearch instance
- ELASTICSEARCH_PASSWORD
  - *string*
  - Password used to authenticate with ElasticSearch instance
- AWS_CREDENTIALS
  - *dict*
  - Dictionary containing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. Used to authenticate with S3 for download and upload.

## Key Values
This flow is dependent on the following key value pairs being present:

- ELASTICSEARCH_HOST
  - *string*
  - URL of ElasticSearch instance for upload
- MESSAGE_BUCKET
  - *string*
  - Name S3 bucket for upload of completion or failure messages

## Flow Parameters
This flow has several parameters that can be passed in at run time:
- canvas_id
  - *string*
  - ID of the canvas to be loaded
- files
  - *List[dict]*
  - List of files to be processed into a canvas in the format:
    -   [
            {
                "name": "mce_canvas_1234",
                "loc": "/canvas_dir/mce_canvas_1234",
                "date": "01/01/2021"
            },
            {
                "name": "canvas_3456",
                "loc": "/canvas_dir/canvas_3456",
                "date": "01/01/2017"
            },
            {
                "name": "mce_canvas_789",
                "loc": "/canvas_dir/mce_canvas_789",
                "date": "01/01/2020"
            }
        ]
- engagement_id
  - *string*
  - ID of the parent engagement and therefore index for this flow to load to
- routing_value
  - *string*
  - ID for shard routing
