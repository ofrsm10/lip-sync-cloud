from texts import S3_BUCKET_NAME
import boto3

def clear_bucket():
    s3_resource = boto3.resource('s3')
    s3_client = boto3.client("s3")

    objects = s3_client.list_objects(Bucket=S3_BUCKET_NAME)['Contents']
    for obj in objects:
        key = obj['Key']
        folder = key.split('/')[0]

        if folder in ['Sessions']:
            bucket = s3_resource.Bucket(S3_BUCKET_NAME)
            bucket.objects.filter(Prefix=key).delete()

    print('Folders deleted from the bucket:', S3_BUCKET_NAME)
    print('Folder cleanup completed.')
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key='Sessions/')
