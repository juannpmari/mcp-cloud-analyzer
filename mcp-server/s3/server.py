import hashlib
from typing import List, Dict, Any, Optional
from utils import hash_object, get_s3_client
from mcp.server.fastmcp import FastMCP
# Create an MCP server
mcp = FastMCP("Cloud analyzer")


# @mcp.resource("s3://{bucket}") #TODO: check if this is useful
# def s3_resource(bucket: str) -> str:
#     """Provide S3 client as a resource."""
#     return get_s3_client()

s3 = get_s3_client()

@mcp.tool()
def list_buckets() -> List[str]:
    """
    Returns a list of bucket names.
    """
    buckets = s3.list_buckets()['Buckets']
    return [b['Name'] for b in buckets]

@mcp.tool()
def list_objects(bucket: str) -> List[Dict[str, Any]]:
    """
    Returns a list of objects in the specified bucket.
    """
    response = s3.list_objects_v2(Bucket=bucket)
    return response.get('Contents', [])

@mcp.tool()
def get_bucket_lifecycle_configuration(bucket: str) -> Dict[str, Any]:
    try:
        response = s3.get_bucket_lifecycle_configuration(Bucket=bucket)
        rules = response.get('Rules', [])
        return rules
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
            return []
        raise

@mcp.tool()
def put_bucket_lifecycle_configuration(bucket: str, rules: List[Dict[str, Any]]) -> None:
    s3.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration={'Rules': rules})

@mcp.tool()
def get_bucket_versioning(bucket: str) -> Dict[str, Any]:
    try:
        response = s3.get_bucket_versioning(Bucket=bucket)
        return response.get('Status', 'Disabled')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketVersioningConfiguration':
            return 'Disabled'
        raise

@mcp.tool()
def put_bucket_versioning(bucket: str, status: str = 'Enabled') -> None:
    s3.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={'Status': status})

@mcp.tool()
def get_bucket_encryption(bucket: str) -> Dict[str, Any]:
    try:
        response = s3.get_bucket_encryption(Bucket=bucket)
        rules = response['ServerSideEncryptionConfiguration']['Rules']

        for rule in rules:
            algorithm = rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']
            kms_key = rule['ApplyServerSideEncryptionByDefault'].get('KMSMasterKeyID')
            print(f"Encryption algorithm: {algorithm}")
            if algorithm == 'aws:kms':
                print(f"KMS Key ID: {kms_key}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            return 'No server-side encryption configured'
        raise

@mcp.tool()
def put_bucket_encryption(bucket: str, rules: List[Dict[str, Any]]) -> None:
    s3.put_bucket_encryption(Bucket=bucket, ServerSideEncryptionConfiguration={'Rules': rules})

@mcp.tool()
def find_duplicates() -> Dict[str, List[tuple]]:
    """
    Finds duplicate objects across all buckets by hash.
    Returns a dict: {hash: [(bucket, key), ...]}
    """
    duplicates = {}
    hash_map = {}
    for bucket in list_buckets(s3):
        for obj in list_objects(s3, bucket):
            key = obj['Key']
            file_hash = hash_object(s3, bucket, key)
            if file_hash in hash_map:
                duplicates.setdefault(file_hash, [hash_map[file_hash]]).append((bucket, key))
            else:
                hash_map[file_hash] = (bucket, key)
    return duplicates

@mcp.prompt()
def optimize_guidelines(s3_guidelines:str) -> str:
    """
    Optimizes the given S3 guidelines based on best practices.
    """
    return f"Improve the following S3 guidelines: {s3_guidelines}"


# Run the server
if __name__ == "__main__":
    mcp.run()#transport='sse', port=3001)