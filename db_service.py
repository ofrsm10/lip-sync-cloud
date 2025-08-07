import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError

from config import CHAT_TABLE, USER_NAME, ADMIN

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
try:
    db_source = boto3.resource('dynamodb')
    logger.info("DynamoDB resource initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DynamoDB resource: {e}")
    raise


def get_from_chat_db(data: str, username: str) -> Optional[Any]:
    """
    Retrieve a specific data field for a user from the chat database.
    
    Args:
        data: The field name to retrieve (e.g., 'state', 'gender')
        username: The user identifier
        
    Returns:
        The value of the requested field, or None if not found
    """
    logger.info(f"Retrieving {data} for user: {username}")
    
    try:
        chat_table = db_source.Table(CHAT_TABLE)
        retrieved_item = run_get_loop(chat_table, {USER_NAME: username})
        
        if retrieved_item:
            value = retrieved_item.get(data)
            logger.info(f"Retrieved {data} = {value} for user: {username}")
            return value
        else:
            logger.info(f"No data found for user: {username}")
            return None
            
    except Exception as e:
        logger.error(f"Error retrieving {data} for user {username}: {e}")
        return None


def update_chat_db(data_values: Dict[str, Any], username: str) -> bool:
    """
    Update multiple attributes for a user in the chat database.
    
    Args:
        data_values: Dictionary of attribute names and values to update
        username: The user identifier
        
    Returns:
        True if update was successful, False otherwise
    """
    logger.info(f"Updating attributes in ChatDB for user: {username}")
    logger.info(f"Attributes to update: {data_values}")
    
    if not data_values:
        logger.warning("No data values provided for update")
        return False
    
    try:
        chat_table = db_source.Table(CHAT_TABLE)
        
        # Retry logic for DynamoDB operations
        for attempt in range(5):
            try:
                update_expression = 'SET ' + ', '.join([f'#{attr} = :{attr}' for attr in data_values.keys()])
                expression_attribute_values = {f':{attr}': value for attr, value in data_values.items()}
                expression_attribute_names = {f'#{attr}': attr for attr in data_values.keys()}

                response = chat_table.update_item(
                    Key={USER_NAME: username},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attribute_values,
                    ExpressionAttributeNames=expression_attribute_names,
                    ReturnValues='UPDATED_NEW'
                )

                if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                    updated_attributes = response.get('Attributes', {})
                    logger.info(f"Successfully updated attributes: {updated_attributes}")
                    return True
                else:
                    logger.warning(f"Unexpected response status on attempt {attempt + 1}")
                    
            except ClientError as e:
                error_code = e.response['Error']['Code']
                logger.warning(f"DynamoDB error on attempt {attempt + 1}: {error_code}")
                
                if error_code in ['ProvisionedThroughputExceededException', 'ThrottlingException']:
                    # Retry for throttling errors
                    continue
                else:
                    # Don't retry for other client errors
                    logger.error(f"Non-retryable DynamoDB error: {e}")
                    return False
            except Exception as e:
                logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
                continue

        logger.error(f"Failed to update attributes after 5 attempts for user: {username}")
        return False
        
    except Exception as e:
        logger.error(f"Error updating chat DB for user {username}: {e}", exc_info=True)
        return False


def delete_conversation(username: str) -> bool:
    """
    Delete a user's conversation data from the chat database.
    
    Args:
        username: The user identifier to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    logger.info(f"Deleting user conversation: {username}")
    
    try:
        chat_table = db_source.Table(CHAT_TABLE)
        response = chat_table.delete_item(Key={USER_NAME: username})
        
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            logger.info(f"Successfully deleted conversation for user: {username}")
            return True
        else:
            logger.error(f"Failed to delete conversation for user: {username}")
            return False
            
    except ClientError as e:
        logger.error(f"DynamoDB error deleting user {username}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting user {username}: {e}")
        return False


def clear_chat_table() -> None:
    """
    Clear all user conversations from the chat table except admin users.
    
    This function scans the entire chat table and deletes all items
    except those belonging to admin users. Use with caution as this
    operation cannot be undone.
    """
    logger.info("Starting chat table cleanup")
    
    try:
        chat_table = db_source.Table(CHAT_TABLE)
        
        # Scan the table to get all items
        response = chat_table.scan()
        items = response['Items']
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = chat_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        deletion_count = 0
        for item in items:
            username = item.get(USER_NAME)
            if username == ADMIN:
                logger.info(f"Skipping admin user: {username}")
                continue
                
            try:
                chat_table.delete_item(Key={USER_NAME: username})
                deletion_count += 1
                logger.info(f"Deleted item: {username}")
            except Exception as e:
                logger.error(f"Failed to delete item {username}: {e}")
                
        logger.info(f"Chat table cleanup completed. Deleted {deletion_count} items.")
        
    except Exception as e:
        logger.error(f"Error during chat table cleanup: {e}", exc_info=True)
        raise


def run_get_loop(table: Any, key: Dict[str, Any], max_attempts: int = 2) -> Optional[Dict[str, Any]]:
    """
    Retrieve an item from DynamoDB table with retry logic.
    
    Args:
        table: DynamoDB table resource
        key: Primary key to retrieve
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Retrieved item as dictionary, or None if not found
    """
    logger.info(f"Attempting to retrieve item with key: {key}")
    
    for attempt in range(max_attempts):
        try:
            response = table.get_item(Key=key)
            
            if 'Item' in response:
                item = response['Item']
                logger.info(f"Successfully retrieved item: {item}")
                return item
            else:
                logger.info("Item not found in table")
                return None
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.warning(f"DynamoDB error on attempt {attempt + 1}: {error_code}")
            
            if attempt == max_attempts - 1:  # Last attempt
                logger.error(f"Failed to retrieve item after {max_attempts} attempts: {e}")
                return None
                
        except Exception as e:
            logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            if attempt == max_attempts - 1:  # Last attempt
                logger.error(f"Failed to retrieve item after {max_attempts} attempts: {e}")
                return None

    return None
