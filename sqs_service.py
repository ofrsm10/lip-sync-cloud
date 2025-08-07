import boto3
import logging
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

from config import QUEUE_URL

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def get_first_sentence_from_queue() -> Optional[str]:
    """
    Retrieve the first sentence from the SQS queue with receive count monitoring.
    
    This function gets a message from the queue and tracks how many times
    it has been received. If a message has been received more than 10 times,
    it is deleted from the queue to prevent infinite processing loops.
    
    Returns:
        The sentence text from the queue, or None if no messages available
        
    Raises:
        ClientError: If SQS operations fail
        NoCredentialsError: If AWS credentials are not configured
    """
    logger.info("Retrieving first sentence from SQS queue")
    
    try:
        sqs = boto3.client('sqs')

        # Receive messages from the queue
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            AttributeNames=['ApproximateReceiveCount'],
            WaitTimeSeconds=5  # Short poll to improve efficiency
        )

        # Check if any messages are received
        if 'Messages' in response:
            message = response['Messages'][0]
            sentence = message['Body']
            
            receive_count = int(message['Attributes']['ApproximateReceiveCount'])
            logger.info(f"Processing sentence: {sentence}")
            logger.info(f"Receive count: {receive_count}")
            
            # Delete messages that have been received too many times
            if receive_count > 10:
                receipt_handle = message['ReceiptHandle']
                try:
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=receipt_handle
                    )
                    logger.warning(f"Deleted message after {receive_count} receives: {sentence}")
                except ClientError as e:
                    logger.error(f"Failed to delete message: {e}")

            return sentence
            
        else:
            logger.info("No messages available in queue")
            return None
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"SQS error getting first sentence: {error_code}")
        raise
    except NoCredentialsError:
        logger.error("AWS credentials not configured")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting first sentence: {e}", exc_info=True)
        raise


def get_next_sentence_from_queue() -> Optional[str]:
    """
    Get the next sentence from the queue and immediately delete it.
    
    This function receives a message with immediate visibility (timeout=0)
    and deletes it from the queue after processing. This ensures each
    sentence is processed only once.
    
    Returns:
        The sentence text from the queue, or None if no messages available
        
    Raises:
        ClientError: If SQS operations fail
        NoCredentialsError: If AWS credentials are not configured
    """
    logger.info("Getting next sentence from SQS queue")
    
    try:
        sqs = boto3.client('sqs')

        # Receive messages from the queue with immediate visibility
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        # Check if any messages are received
        if 'Messages' in response:
            message = response['Messages'][0]
            sentence = message['Body']

            logger.info(f"Processing sentence: {sentence}")

            # Delete the message from the queue
            receipt_handle = message['ReceiptHandle']
            try:
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                logger.info(f"Successfully processed and deleted message: {sentence}")
            except ClientError as e:
                logger.error(f"Failed to delete message: {e}")
                # Return the sentence anyway since we processed it

            return sentence
        else:
            logger.info("No unreceived sentences in the queue")
            return None
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"SQS error getting next sentence: {error_code}")
        raise
    except NoCredentialsError:
        logger.error("AWS credentials not configured")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting next sentence: {e}", exc_info=True)
        raise
