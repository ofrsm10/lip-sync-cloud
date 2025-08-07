import json
import logging
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from config import STATE, USER_NAME, get_env_var

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Get Hermes Lambda function name from environment
HERMES_FUNCTION_NAME = get_env_var('HERMES_LAMBDA_FUNCTION_NAME', 'HermesDayJob')


def invoke_second_lambda(parameters: List[str], state: str) -> Dict[str, Any]:
    """
    Invoke the Hermes Lambda function for video processing.
    
    This function triggers the video processing pipeline by invoking
    a separate Lambda function (Hermes) that handles video download
    and processing operations.
    
    Args:
        parameters: List containing [username, file_id] for video processing
        state: Current conversation state
        
    Returns:
        Dictionary with statusCode and body indicating success or failure
        
    Raises:
        ClientError: If Lambda invocation fails
        NoCredentialsError: If AWS credentials are not configured
    """
    logger.info("Invoking Hermes Lambda for video processing")
    
    if len(parameters) < 2:
        logger.error("Insufficient parameters provided for Lambda invocation")
        return {
            'statusCode': 400,
            'body': 'Invalid parameters for video processing'
        }
    
    username, file_id = parameters[0], parameters[1]
    logger.info(f"Processing video for user: {username}, file_id: {file_id}")
    
    try:
        lambda_client = boto3.client('lambda')
        
        payload = {
            STATE: state,
            USER_NAME: username,
            "file_id": file_id
        }
        payload_json = json.dumps(payload)
        
        logger.info(f"Lambda payload: {payload}")

        params = {
            'FunctionName': HERMES_FUNCTION_NAME,
            'InvocationType': 'Event',  # Invoke asynchronously
            'Payload': payload_json,
        }
        
        response = lambda_client.invoke(**params)
        
        # Check if invocation was successful
        status_code = response.get('StatusCode', 0)
        if status_code == 202:  # Accepted for async invocation
            logger.info("Hermes Lambda function triggered successfully")
            return {
                'statusCode': 200,
                'body': 'Video processing initiated successfully',
            }
        else:
            logger.error(f"Lambda invocation returned unexpected status: {status_code}")
            return {
                'statusCode': 500,
                'body': 'Failed to trigger video processing',
            }
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"AWS Lambda error invoking {HERMES_FUNCTION_NAME}: {error_code}")
        return {
            'statusCode': 500,
            'body': f'AWS error: {error_code}',
        }
    except NoCredentialsError:
        logger.error("AWS credentials not configured")
        return {
            'statusCode': 500,
            'body': 'AWS credentials not configured',
        }
    except Exception as e:
        logger.error(f"Unexpected error invoking Hermes Lambda: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': 'Internal error during video processing',
        }
