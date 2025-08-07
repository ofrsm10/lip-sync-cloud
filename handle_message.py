import logging
from typing import Optional

from db_service import update_chat_db
from handle_callback import handle_none
from config import (
    CONFIG, VIP_USER_MENU, VIP_USER_SENTENCE, AGE, ACCENT, 
    VIP_USER_GET_SENTENCE, STATE, SENTENCE, LIGHTING_COLOR, 
    LIGHTING_INTENSITY, PLACE, ADMIN
)
from send_options import (
    send_config_message, send_config_menu, send_accent_question, 
    send_default_response, send_lighting_intensity_question, 
    send_lighting_color_question, send_vip_user_menu, 
    send_vip_user_sentence_video_instructions, send_wrong_response_message
)

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


async def handle_message(text_message: str, username: str, state: Optional[str]) -> None:
    """
    Handle incoming text messages based on current conversation state.
    
    This function processes text messages from users and routes them to
    appropriate handlers based on the current conversation state and
    user permissions.
    
    Args:
        text_message: The text content of the user's message
        username: The user identifier
        state: Current conversation state (can be None for new conversations)
    """
    logger.info(f"Processing text message from {username}: {text_message}")
    logger.info(f"Current conversation state: {state}")

    # Admin configuration command
    if text_message.lower().startswith(CONFIG.lower()) and username == ADMIN:
        logger.info(f"Admin {username} accessing configuration")
        success = update_chat_db({STATE: CONFIG}, username)
        if success:
            await send_config_message()
            await send_config_menu()
        else:
            logger.error(f"Failed to update state to CONFIG for admin {username}")
            await send_default_response()

    # New conversation or restart command
    elif state is None or text_message == "חדש":
        logger.info(f"Starting new conversation for user: {username}")
        await handle_none("new")

    # Age input handling
    elif state == AGE:
        logger.info(f"Processing age input: {text_message}")
        if text_message.isdigit():
            age = int(text_message)
            if 16 <= age <= 120:  # Basic age validation
                success = update_chat_db({AGE: age, STATE: ACCENT}, username)
                if success:
                    await send_accent_question()
                else:
                    logger.error(f"Failed to update age for user {username}")
                    await send_default_response()
            else:
                logger.warning(f"Invalid age provided by {username}: {age}")
                await send_default_response()
        else:
            logger.warning(f"Non-numeric age input from {username}: {text_message}")
            await send_default_response()

    # Location/place input handling
    elif state == PLACE:
        logger.info(f"Processing place input: {text_message}")
        if text_message.strip():  # Ensure non-empty input
            success = update_chat_db({PLACE: text_message.strip(), STATE: LIGHTING_INTENSITY}, username)
            if success:
                await send_lighting_intensity_question()
            else:
                logger.error(f"Failed to update place for user {username}")
                await send_default_response()
        else:
            logger.warning(f"Empty place input from {username}")
            await send_default_response()

    # Lighting intensity input handling
    elif state == LIGHTING_INTENSITY:
        logger.info(f"Processing lighting intensity input: {text_message}")
        if text_message.isdigit():
            intensity = int(text_message)
            if 1 <= intensity <= 10:  # Validate intensity range
                success = update_chat_db({LIGHTING_INTENSITY: str(intensity), STATE: LIGHTING_COLOR}, username)
                if success:
                    await send_lighting_color_question()
                else:
                    logger.error(f"Failed to update lighting intensity for user {username}")
                    await send_default_response()
            else:
                logger.warning(f"Invalid lighting intensity from {username}: {intensity}")
                await send_default_response()
        else:
            logger.warning(f"Non-numeric lighting intensity from {username}: {text_message}")
            await send_default_response()

    # Lighting color input handling
    elif state == LIGHTING_COLOR:
        logger.info(f"Processing lighting color input: {text_message}")
        if text_message.strip():  # Ensure non-empty input
            success = update_chat_db({LIGHTING_COLOR: text_message.strip(), STATE: VIP_USER_MENU}, username)
            if success:
                await send_vip_user_menu()
            else:
                logger.error(f"Failed to update lighting color for user {username}")
                await send_default_response()
        else:
            logger.warning(f"Empty lighting color input from {username}")
            await send_default_response()

    # Sentence input for VIP users
    elif state == VIP_USER_GET_SENTENCE:
        logger.info(f"Processing sentence input: {text_message}")
        if text_message.strip():  # Ensure non-empty sentence
            success = update_chat_db({SENTENCE: text_message.strip(), STATE: VIP_USER_SENTENCE}, username)
            if success:
                await send_vip_user_sentence_video_instructions(text_message.strip())
            else:
                logger.error(f"Failed to update sentence for user {username}")
                await send_default_response()
        else:
            logger.warning(f"Empty sentence input from {username}")
            await send_default_response()
            
    else:
        logger.warning(f"Unhandled message state {state} from user {username}: {text_message}")
        await send_wrong_response_message()
