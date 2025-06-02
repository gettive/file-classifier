import boto3
import os
import urllib.request
import sys
import json

s3 = boto3.client("s3")

IMAGE_BUCKET = os.environ["IMAGE_BUCKET"]
VIDEO_BUCKET = os.environ["VIDEO_BUCKET"]
DOCUMENT_BUCKET = os.environ["DOCUMENT_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
ARCHIVE_BUCKET = os.environ["ARCHIVE_BUCKET"]
DATA_BUCKET = os.environ["DATA_BUCKET"]
CODE_BUCKET = os.environ["CODE_BUCKET"]
OTHER_BUCKET = os.environ["OTHER_BUCKET"]

CATEGORY_BUCKETS = {
    'images': IMAGE_BUCKET,
    'videos': VIDEO_BUCKET,
    'documents': DOCUMENT_BUCKET,
    'audio': AUDIO_BUCKET,
    'archives': ARCHIVE_BUCKET,
    'data': DATA_BUCKET,
    'code': CODE_BUCKET,
    'other': OTHER_BUCKET,
}

def get_category(bucket, key):
    response = s3.head_object(Bucket=bucket, Key=key)
    mime_type = response['ContentType']

    if mime_type is None:
        return 'other'

    if mime_type.startswith('image/'):
        return 'images'
    elif mime_type.startswith('video/'):
        return 'videos'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf', 'application/msword',
                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                       'text/plain', 'application/rtf', 'text/markdown']:
        return 'documents'
    elif mime_type in ['application/zip', 'application/x-tar', 'application/x-7z-compressed',
                       'application/x-rar-compressed', 'application/gzip']:
        return 'archives'
    elif mime_type in ['application/json', 'text/csv', 'application/xml', 'application/yaml', 'text/yaml']:
        return 'data'
    elif mime_type.startswith('text/') or mime_type == 'application/javascript':
        return 'code'
    else:
        return 'other'
        

def lambda_handler(event, context=None):
    
    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        source_object_key = record["s3"]["object"]["key"]

        if not OTHER_BUCKET:
            raise ValueError("Expects 'Other' bucket to be available")
        elif source_bucket == dest_bucket or :
            raise ValueError("Can't reuse source bucket as a destination")

        category = get_category(source_bucket, source_object_key)
        dest_bucket = CATEGORY_BUCKETS[category]

        if not dest_bucket:
            dest_bucket = OTHER_BUCKET

        print(f"Copying '{src_key}' to '{dest_bucket}' under category '{category}'")

        s3.copy_object(
            Bucket=dest_bucket,
            CopySource={'Bucket': source_bucket, 'Key': source_object_key},
            Key=src_key
        )

    return {"statusCode": 200, "body": "Files copied successfully"}


if __name__ == "__main__":
    AWS_LAMBDA_RUNTIME_API = os.environ["AWS_LAMBDA_RUNTIME_API"]
    while True:
        url = f"http://{AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/next"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            headers = dict(response.getheaders())
            event_body = json.loads(response.read().decode())

        request_id = headers["Lambda-Runtime-Aws-Request-Id"]
        result = lambda_handler(event_body)

        payload = json.dumps(result).encode('utf-8')
        post_url = f"http://{AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/{request_id}/response"
        post_req = urllib.request.Request(
                post_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
        with urllib.request.urlopen(post_req) as _:
            pass


