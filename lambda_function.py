import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

import requests
from telegram import Bot

from db_service import db_source, run_get_loop
from handle_callback import handle_callback_query
from handle_message import handle_message
from handle_video import handle_video
from send_options import send_initial_vip_user, send_place_question, \
    send_gender_question, \
    send_wrong_response_message
from config import (
    GENDER, AGE, ACCENT, STATE, USER_NAME, SESSION_ID, 
    LIGHTING_COLOR, LIGHTING_INTENSITY, PLACE, TTL, MALE, 
    VIP_USER, CHAT_TABLE, TOKEN
)

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# globals
chat_id = None
username = None
state = None
gender = None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing Telegram webhook events.
    
    This function handles incoming Telegram bot messages and callbacks,
    processing them through the conversation flow for lip-sync data collection.
    
    Args:
        event: AWS Lambda event containing the Telegram webhook payload
        context: AWS Lambda context object (unused but required)
        
    Returns:
        Dict containing HTTP status code response
    """
    logger.info("#################### New event ###########################")
    try:
        if 'body' not in event:
            logger.error("Missing body in event")
            return {'statusCode': 400, 'body': 'Missing body in request'}
            
        body = json.loads(event['body'])
        logger.info(f"Processing webhook body: {json.dumps(body, ensure_ascii=False)}")
        
        asyncio.run(process(body))
        logger.info("Event processed successfully")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {'statusCode': 400, 'body': 'Invalid JSON in request body'}
    except Exception as e:
        logger.error(f"Unexpected error processing event: {e}", exc_info=True)
        return {'statusCode': 500, 'body': 'Internal server error'}
        
    return {'statusCode': 200}


def get_user_info(body: Dict[str, Any]) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract user information from Telegram webhook body.
    
    Handles both regular messages and callback queries to extract
    the chat ID and username for user identification.
    
    Args:
        body: Telegram webhook body containing message or callback_query
        
    Returns:
        Tuple of (chat_id, username) where both can be None if not found
        
    Raises:
        ValueError: If neither message nor callback_query is found in body
    """
    logger.info("Extracting chat_id and username from webhook body")
    
    if 'message' in body:
        message = body.get('message', {})
        chat = message.get('chat', {})
        from_user = message.get('from', {})
        
        chat_id = chat.get('id')
        username = from_user.get('username')
        
    elif 'callback_query' in body:
        callback_query = body.get('callback_query', {})
        message = callback_query.get('message', {})
        chat = message.get('chat', {})
        from_user = callback_query.get('from', {})
        
        chat_id = chat.get('id')
        username = from_user.get('username')
        
    else:
        logger.error("No message or callback_query found in body")
        raise ValueError("Invalid webhook body: missing message or callback_query")
    
    logger.info(f"Extracted user info - chat_id: {chat_id}, username: {username}")
    return chat_id, username


async def process(body: Dict[str, Any]) -> None:
    """
    Process incoming Telegram webhook body and route to appropriate handlers.
    
    This function manages the conversation state and routes messages or 
    callback queries to the appropriate handlers based on the content type.
    
    Args:
        body: Telegram webhook body containing the update
    """
    global chat_id, username, state, gender

    try:
        chat_id, username = get_user_info(body)
    except ValueError as e:
        logger.error(f"Failed to extract user info: {e}")
        return
        
    if not chat_id:
        logger.error("No chat_id found in request")
        return
    
    # Use chat_id as username fallback if username is not available
    if not username:
        username = str(chat_id)
        logger.info(f"Using chat_id as username: {username}")

    # Load conversation state from database
    chat_table = db_source.Table(CHAT_TABLE)
    conversation = run_get_loop(chat_table, {USER_NAME: username})
    
    if conversation:
        state = conversation.get(STATE)
        if username != VIP_USER:
            gender = conversation.get(GENDER)

    logger.info(f"Current conversation state: {state}")
    logger.info(f"Processing for user: {username}")
    
    # Initialize Telegram bot and send typing indicator
    try:
        bot = Bot(TOKEN)
        await bot.send_chat_action(chat_id, 'typing')
    except Exception as e:
        logger.error(f"Failed to send typing indicator: {e}")

    # Route based on message type
    if 'message' in body:
        message = body['message']
        text = message.get('text')
        video_info = message.get('video')
        video_file_id = video_info.get('file_id') if video_info else None

        if text:
            logger.info(f"Processing text message: {text}")
            await handle_message(text, username, state)

        elif video_file_id:
            logger.info(f"Processing video message with file_id: {video_file_id}")
            await handle_video(video_file_id, state)
        else:
            logger.warning("Message contains neither text nor video")
            await send_wrong_response_message()

    elif 'callback_query' in body:
        callback_query = body['callback_query']
        data = callback_query.get('data')
        if data:
            logger.info(f"Processing callback query: {data}")
            await handle_callback_query(data)
        else:
            logger.warning("Callback query missing data")
            await send_wrong_response_message()

    else:
        logger.warning("No text, video, or callback query in webhook body")
        await send_wrong_response_message()


def get_file_url(file_id: str) -> str:
    """
    Get the download URL for a Telegram file using the bot's file API.
    
    Args:
        file_id: Telegram file identifier
        
    Returns:
        Complete URL to download the file from Telegram servers
        
    Raises:
        requests.RequestException: If the API request fails
        KeyError: If the response doesn't contain expected fields
    """
    logger.info(f"Getting file URL for file_id: {file_id}")
    
    try:
        # Call Telegram Bot API's getFile method to retrieve the file's URL
        response = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getFile", 
            params={'file_id': file_id},
            timeout=30
        )
        response.raise_for_status()
        
        response_json = response.json()
        
        if not response_json.get('ok'):
            error_description = response_json.get('description', 'Unknown error')
            raise requests.RequestException(f"Telegram API error: {error_description}")
            
        file_path = response_json['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        
        logger.info(f"Generated file URL: {file_url}")
        return file_url
        
    except requests.RequestException as e:
        logger.error(f"Failed to get file URL: {e}")
        raise
    except KeyError as e:
        logger.error(f"Unexpected response format from Telegram API: {e}")
        raise


async def start_conversation() -> None:
    """
    Initialize a new conversation for a user in the database.
    
    Sets up initial conversation state based on whether the user is a VIP user
    or a regular user. VIP users skip the initial setup questions and go
    directly to the main workflow.
    """
    logger.info(f"Creating new chat entry for user: {username}")
    
    now = datetime.now()
    session_id = now.strftime("%m/%d/%H:%M")
    chat_table = db_source.Table(CHAT_TABLE)

    try:
        if username == VIP_USER:
            # VIP users get pre-configured settings and skip initial questions
            attribute_updates = {
                STATE: PLACE, 
                GENDER: MALE, 
                AGE: '51', 
                ACCENT: 'none',
                LIGHTING_INTENSITY: '0', 
                LIGHTING_COLOR: 'none'
            }
            await send_initial_vip_user()
            await send_place_question()
        else:
            # Regular users go through the full onboarding flow
            current_time = int(time.time())
            expiration_time = current_time + (10 * 60)  # 10 minutes TTL
            
            attribute_updates = {
                STATE: GENDER, 
                GENDER: 'none', 
                AGE: '0', 
                ACCENT: 'none',
                SESSION_ID: session_id, 
                TTL: expiration_time
            }
            await send_gender_question()

        # Update user record in DynamoDB
        update_expression = 'SET ' + ', '.join([f'#{attr} = :{attr}' for attr in attribute_updates.keys()])
        expression_attribute_values = {f':{attr}': value for attr, value in attribute_updates.items()}
        expression_attribute_names = {f'#{attr}': attr for attr in attribute_updates.keys()}

        response = chat_table.update_item(
            Key={USER_NAME: username},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues='UPDATED_NEW'
        )

        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            updated_attributes = response.get('Attributes', {})
            logger.info(f"Successfully updated user attributes: {updated_attributes}")
        else:
            logger.error(f"Failed to set user chat data for: {username}")
            
    except Exception as e:
        logger.error(f"Error starting conversation for user {username}: {e}", exc_info=True)
        raise


def gender_suitable_text(receive_ok_terms: str) -> None:
    """
    Placeholder function for gender-specific text processing.
    
    Args:
        receive_ok_terms: Terms acceptance message text
        
    Note:
        This function appears to be incomplete in the original code.
        It should be implemented based on specific requirements.
    """
    # TODO: Implement gender-specific text processing logic
    pass
