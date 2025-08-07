import logging
from typing import Optional, Dict, Callable, Any

from handle_callback import handle_none
from sqs_service import get_first_sentence_from_queue
from lambda_service import invoke_second_lambda
from db_service import update_chat_db
from send_options import (
    send_wrong_response_message, send_vip_user_goodbye, send_success_message, 
    send_config_menu, send_nth_video_menu, send_second_video_instructions
)
from config import (
    FIRST_VIDEO, SECOND_VIDEO, NTH_VIDEO, CONFIG, VIP_USER_SENTENCE, 
    VIP_USER_CALIB, STATE, LAST_CHOICE
)

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


async def handle_video(video_file_id: str, username: str, state: Optional[str]) -> None:
    """
    Handle incoming video messages based on current conversation state.
    
    This function routes video messages to appropriate handlers based on
    the current conversation state. Different states require different
    video processing workflows.
    
    Args:
        video_file_id: Telegram file ID for the uploaded video
        username: User identifier
        state: Current conversation state
    """
    logger.info(f"Processing video from {username} at state: {state}")
    logger.info(f"Video file_id: {video_file_id}")

    # Define state-to-handler mapping
    state_actions: Dict[Optional[str], Callable] = {
        FIRST_VIDEO: handle_first_video,
        SECOND_VIDEO: handle_second_video,
        NTH_VIDEO: handle_second_video,
        CONFIG: handle_config_video,
        VIP_USER_SENTENCE: handle_vip_user_video,
        VIP_USER_CALIB: handle_vip_user_video,
        None: handle_none,
    }

    action = state_actions.get(state)
    if action:
        logger.info(f"Routing to handler: {action.__name__}")
        try:
            await action(video_file_id, state, username)
        except Exception as e:
            logger.error(f"Error in video handler {action.__name__}: {e}", exc_info=True)
            await send_wrong_response_message()
    else:
        logger.warning(f"No handler found for state: {state}")
        await send_wrong_response_message()


async def handle_vip_user_video(video_file_id: str, state: str, username: str) -> None:
    """
    Handle video uploads from VIP users.
    
    VIP users can upload calibration videos or sentence videos.
    This function processes their videos and sends a goodbye message.
    
    Args:
        video_file_id: Telegram file ID for the uploaded video
        state: Current conversation state (VIP_USER_SENTENCE or VIP_USER_CALIB)
        username: User identifier
    """
    logger.info(f"Processing VIP user video: {state} from {username}")
    
    try:
        parameters = [username, video_file_id]
        result = invoke_second_lambda(parameters, state)
        
        if result['statusCode'] == 200:
            logger.info(f"Successfully initiated video processing for VIP user {username}")
            await send_vip_user_goodbye()
        else:
            logger.error(f"Failed to process VIP user video: {result}")
            await send_wrong_response_message()
            
    except Exception as e:
        logger.error(f"Error processing VIP user video: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_config_video(video_file_id: str, state: str, username: str) -> None:
    """
    Handle video uploads in configuration mode (admin only).
    
    Admin users can upload videos for testing or configuration purposes.
    
    Args:
        video_file_id: Telegram file ID for the uploaded video
        state: Current conversation state (CONFIG)
        username: User identifier
    """
    logger.info(f"Processing config video from {username}")
    
    try:
        parameters = [username, video_file_id]
        result = invoke_second_lambda(parameters, state)
        
        if result['statusCode'] == 200:
            logger.info(f"Successfully initiated config video processing for {username}")
            await send_success_message()
            await send_config_menu()
        else:
            logger.error(f"Failed to process config video: {result}")
            await send_wrong_response_message()
            
    except Exception as e:
        logger.error(f"Error processing config video: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_second_video(video_file_id: str, state: str, username: str) -> None:
    """
    Handle second video uploads (sentence videos) from regular users.
    
    This function processes sentence videos and transitions to the
    choice menu for additional contributions.
    
    Args:
        video_file_id: Telegram file ID for the uploaded video
        state: Current conversation state (SECOND_VIDEO or NTH_VIDEO)
        username: User identifier
    """
    logger.info(f"Processing second/nth video from {username}")
    
    try:
        parameters = [username, video_file_id]
        result = invoke_second_lambda(parameters, state)
        
        if result['statusCode'] == 200:
            logger.info(f"Successfully initiated video processing for {username}")
            
            # Update state to show choice menu
            success = update_chat_db({STATE: LAST_CHOICE}, username)
            if success:
                await send_nth_video_menu()
            else:
                logger.error(f"Failed to update state for user {username}")
                await send_wrong_response_message()
        else:
            logger.error(f"Failed to process second video: {result}")
            await send_wrong_response_message()
            
    except Exception as e:
        logger.error(f"Error processing second video: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_first_video(video_file_id: str, state: str, username: str) -> None:
    """
    Handle first video uploads (calibration videos) from regular users.
    
    This function processes calibration videos and transitions to
    the second video state with a sentence from the queue.
    
    Args:
        video_file_id: Telegram file ID for the uploaded video
        state: Current conversation state (FIRST_VIDEO)
        username: User identifier
    """
    logger.info(f"Processing first video from {username}")
    
    try:
        parameters = [username, video_file_id]
        result = invoke_second_lambda(parameters, state)
        
        if result['statusCode'] == 200:
            logger.info(f"Successfully initiated calibration video processing for {username}")
            
            # Update state to second video
            success = update_chat_db({STATE: SECOND_VIDEO}, username)
            if not success:
                logger.error(f"Failed to update state for user {username}")
                await send_wrong_response_message()
                return
            
            # Get sentence from queue for second video
            try:
                sentence = get_first_sentence_from_queue()
                if sentence:
                    logger.info(f"Retrieved sentence for {username}: {sentence}")
                    await send_second_video_instructions(sentence)
                else:
                    logger.warning("No sentence available in queue")
                    await send_wrong_response_message()
            except Exception as e:
                logger.error(f"Error getting sentence from queue: {e}")
                await send_wrong_response_message()
                
        else:
            logger.error(f"Failed to process first video: {result}")
            await send_wrong_response_message()
            
    except Exception as e:
        logger.error(f"Error processing first video: {e}", exc_info=True)
        await send_wrong_response_message()
