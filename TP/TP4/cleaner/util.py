
import os, io, json
import boto3
from botocore.client import Config

def s3_client():
    endpoint = os.getenv("S3_URL", "http://minio:9000")
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )

def put_object_bytes(bucket, key, data: bytes, content_type="application/octet-stream"):
    s3 = s3_client()
    s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)

def get_object_bytes(bucket, key) -> bytes:
    s3 = s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()

def list_objects(bucket, prefix=""):
    s3 = s3_client()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for c in page.get("Contents", []):
            yield c["Key"]

def copy_then_delete(src_bucket, src_key, dst_bucket, dst_key):
    s3 = s3_client()
    s3.copy_object(
        Bucket=dst_bucket,
        CopySource={"Bucket": src_bucket, "Key": src_key},
        Key=dst_key
    )
    s3.delete_object(Bucket=src_bucket, Key=src_key)
