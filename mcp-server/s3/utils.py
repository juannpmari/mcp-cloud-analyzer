import boto3

def get_s3_client(
    aws_access_key_id: str = 'test',
    aws_secret_access_key: str = 'test',
    region_name: str = 'us-east-1',
    endpoint_url: str = 'http://localhost:4566'
) -> boto3.client:
    """
    Returns a boto3 S3 client for Localstack or AWS.
    """
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        endpoint_url=endpoint_url
    )


def create_bucket(s3, bucket_name: str) -> None:
    """
    Creates a bucket with the given name.
    """
    s3.create_bucket(Bucket=bucket_name)


def put_object(s3, bucket: str, key: str, body: str) -> None:
    """
    Uploads an object to the specified bucket.
    """
    s3.put_object(Bucket=bucket, Key=key, Body=body)

def hash_object(s3, bucket: str, key: str) -> str:
    """
    Returns the MD5 hash of the object's body.
    """
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()
    return hashlib.md5(body).hexdigest()