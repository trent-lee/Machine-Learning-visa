import os
from typing import Any

try:
    import boto3
except ModuleNotFoundError:  # pragma: no cover - runtime fallback
    boto3 = None

from us_visa.constants import AWS_SECRET_ACCESS_KEY_ENV_KEY, AWS_ACCESS_KEY_ID_ENV_KEY, REGION_NAME


class S3Client:

    s3_client = None
    s3_resource = None

    def __init__(self, region_name=REGION_NAME):
        """
        This Class gets aws credentials from env_variable and creates a connection with S3 when
        credentials are available. If the credentials are missing, it leaves the client unset so
        the application can fall back to local artifacts.
        """

        if S3Client.s3_resource is None or S3Client.s3_client is None:
            access_key_id = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY)
            secret_access_key = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY)

            if boto3 is not None and access_key_id and secret_access_key:
                S3Client.s3_resource = boto3.resource(
                    's3',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region_name,
                )
                S3Client.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region_name,
                )
            else:
                S3Client.s3_resource = None
                S3Client.s3_client = None

        self.s3_resource = S3Client.s3_resource
        self.s3_client = S3Client.s3_client
