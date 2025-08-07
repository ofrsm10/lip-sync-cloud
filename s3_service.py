import boto3
import logging
from typing import List
from botocore.exceptions import ClientError, NoCredentialsError

from config import S3_BUCKET_NAME

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def clear_bucket() -> None:
    """
    Clear specific folders from the S3 bucket while preserving bucket structure.
    
    This function removes all objects from the 'Sessions' folder in the S3 bucket
    and recreates the folder structure. This is used for cleanup operations.
    
    Raises:
        ClientError: If S3 operations fail
        NoCredentialsError: If AWS credentials are not configured
    """
    logger.info(f"Starting S3 bucket cleanup for bucket: {S3_BUCKET_NAME}")
    
    try:
        s3_resource = boto3.resource('s3')
        s3_client = boto3.client('s3')

        # List all objects in the bucket
        try:
            response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
            objects = response.get('Contents', [])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                logger.error(f"S3 bucket does not exist: {S3_BUCKET_NAME}")
                return
            else:
                raise

        deleted_count = 0
        for obj in objects:
            key = obj['Key']
            folder = key.split('/')[0] if '/' in key else key

            # Only delete objects in the Sessions folder
            if folder == 'Sessions':
                try:
                    bucket = s3_resource.Bucket(S3_BUCKET_NAME)
                    # Delete all objects with this prefix
                    bucket.objects.filter(Prefix=key).delete()
                    deleted_count += 1
                    logger.info(f"Deleted object: {key}")
                except ClientError as e:
                    logger.error(f"Failed to delete object {key}: {e}")

        logger.info(f"Deleted {deleted_count} objects from Sessions folder")

        # Recreate the Sessions folder structure
        try:
            s3_client.put_object(Bucket=S3_BUCKET_NAME, Key='Sessions/')
            logger.info("Recreated Sessions/ folder structure")
        except ClientError as e:
            logger.error(f"Failed to recreate Sessions folder: {e}")

        logger.info(f"S3 bucket cleanup completed for: {S3_BUCKET_NAME}")
        
    except NoCredentialsError:
        logger.error("AWS credentials not configured")
        raise
    except ClientError as e:
        logger.error(f"AWS S3 error during bucket cleanup: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during S3 bucket cleanup: {e}", exc_info=True)
        raise
