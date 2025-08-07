import logging
from typing import Optional

from telegram import Bot

from lambda_function import state, username, gender, start_conversation, gender_suitable_text, chat_id
from sqs_service import get_next_sentence_from_queue
from db_service import get_from_chat_db, update_chat_db, delete_conversation
from config import (
    CONFIG, GENDER, TERMS, INIT, VIP_USER_MENU, VIP_USER_CALIB, VIP_USER_SENTENCE, 
    BRIEF, AGE, ACCENT, FIRST_VIDEO, VIP_USER_GET_SENTENCE, SECOND_VIDEO, LAST_CHOICE, 
    NTH_VIDEO, STATE, SENTENCE, LIGHTING_COLOR, LIGHTING_INTENSITY, PLACE, MALE, FEMALE, 
    ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, ACCENT6, ACCENT7, OK_TERMS, OK_NTH, 
    IM_DONE, OK_TERMS_FEMALE, QUIT, WHAT, RESET, BRIEF1, LETSTART, ADMIN, TOKEN, 
    RECEIVE_OK_TERMS, RECEIVE_OK_TERMS_FEMALE, WHAT_TEXT
)
from send_options import (
    send_config_message, send_success_message, send_config_menu, send_briefing_menu,
    send_accent_specific, send_first_video_instructions, send_nth_video_instructions, 
    send_goodbye, send_brief, send_terms, send_age_question, send_vip_user_calib_instructions, 
    send_vip_user_menu, send_place_question, send_lighting_color_question, 
    send_lighting_intensity_question, send_vip_user_sentence_instructions,
    send_vip_user_sentence_video_instructions, send_gender_question, send_accent_question,
    send_second_video_instructions, send_nth_video_menu, send_wrong_response_message
)

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


async def handle_quit_callback(callback_data: str) -> None:
    """
    Handle quit/exit callback from users.
    
    For admin users in config mode, this deletes the conversation.
    For other users, it shows success and config menu.
    
    Args:
        callback_data: The callback data (QUIT)
    """
    logger.info(f"Processing quit callback from {username}")
    
    try:
        if state == CONFIG and username == ADMIN:
            success = delete_conversation(username)
            if success:
                await send_config_message()
            else:
                logger.error(f"Failed to delete conversation for admin {username}")
                await send_wrong_response_message()
        else:
            await send_success_message()
            await send_config_menu()
    except Exception as e:
        logger.error(f"Error handling quit callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_gender_callback(callback_data: str) -> None:
    """
    Handle gender selection callback.
    
    Updates the user's gender preference and moves to briefing stage.
    
    Args:
        callback_data: Gender selection (MALE or FEMALE)
    """
    logger.info(f"Processing gender selection: {callback_data} for {username}")
    
    if callback_data not in [MALE, FEMALE]:
        logger.warning(f"Invalid gender selection: {callback_data}")
        await send_wrong_response_message()
        return
    
    try:
        data_values = {
            GENDER: callback_data,
            STATE: BRIEF,
        }
        success = update_chat_db(data_values, username)
        if success:
            await send_briefing_menu()
        else:
            logger.error(f"Failed to update gender for user {username}")
            await send_wrong_response_message()
    except Exception as e:
        logger.error(f"Error handling gender callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_accent_callback(callback_data: str) -> None:
    """
    Handle accent selection callback.
    
    If user selects "yes" to having an accent, shows specific accent options.
    Otherwise, records the accent choice and moves to video instructions.
    
    Args:
        callback_data: Accent selection option
    """
    logger.info(f"Processing accent selection: {callback_data} for {username}")
    
    valid_accents = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, ACCENT6, ACCENT7]
    if callback_data not in valid_accents:
        logger.warning(f"Invalid accent selection: {callback_data}")
        await send_wrong_response_message()
        return
    
    try:
        if callback_data == ACCENT2:  # "Yes" to having an accent
            await send_accent_specific()
        else:
            data_values = {
                ACCENT: callback_data,
                STATE: FIRST_VIDEO,
            }
            success = update_chat_db(data_values, username)
            if success:
                await send_first_video_instructions()
            else:
                logger.error(f"Failed to update accent for user {username}")
                await send_wrong_response_message()
    except Exception as e:
        logger.error(f"Error handling accent callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_send_video_callback(callback_data: str) -> None:
    """
    Handle request to send additional video callback.
    
    Gets a new sentence from the queue and prepares for nth video upload.
    
    Args:
        callback_data: Callback data (OK_NTH)
    """
    logger.info(f"Processing send video request from {username}")
    
    try:
        sentence = get_next_sentence_from_queue()
        if sentence:
            logger.info(f"Retrieved sentence for {username}: {sentence}")
            await send_nth_video_instructions(sentence)
            
            success = update_chat_db({STATE: NTH_VIDEO, SENTENCE: sentence}, username)
            if not success:
                logger.error(f"Failed to update state for user {username}")
                await send_wrong_response_message()
        else:
            logger.warning("No sentence available in queue")
            await send_wrong_response_message()
    except Exception as e:
        logger.error(f"Error handling send video callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_done_callback(callback_data: str) -> None:
    """
    Handle user indicating they are done contributing.
    
    Deletes the conversation and sends goodbye message.
    
    Args:
        callback_data: Callback data (IM_DONE)
    """
    logger.info(f"Processing done callback from {username}")
    
    try:
        success = delete_conversation(username)
        if success:
            await send_goodbye()
        else:
            logger.error(f"Failed to delete conversation for user {username}")
            await send_goodbye()  # Send goodbye anyway
    except Exception as e:
        logger.error(f"Error handling done callback: {e}", exc_info=True)
        await send_goodbye()  # Send goodbye anyway


async def handle_brief_callback(callback_data: str) -> None:
    """
    Handle briefing request callback.
    
    Sends briefing information to the user.
    
    Args:
        callback_data: Callback data (BRIEF1)
    """
    logger.info(f"Processing briefing request from {username}")
    
    try:
        await send_brief()
    except Exception as e:
        logger.error(f"Error sending briefing: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_letstart_callback(callback_data: str) -> None:
    """
    Handle "let's start" callback.
    
    Moves user to terms acceptance stage.
    
    Args:
        callback_data: Callback data (LETSTART)
    """
    logger.info(f"Processing let's start request from {username}")
    
    try:
        data_values = {STATE: TERMS}
        success = update_chat_db(data_values, username)
        if success:
            await send_terms()
        else:
            logger.error(f"Failed to update state for user {username}")
            await send_wrong_response_message()
    except Exception as e:
        logger.error(f"Error handling let's start callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_ok_terms_callback(callback_data: str) -> None:
    """
    Handle terms acceptance callback.
    
    Updates state to age collection and sends age question with
    gender-appropriate text.
    
    Args:
        callback_data: Callback data (OK_TERMS or OK_TERMS_FEMALE)
    """
    logger.info(f"Processing terms acceptance from {username}")
    
    try:
        success = update_chat_db({STATE: AGE}, username)
        if not success:
            logger.error(f"Failed to update state for user {username}")
            await send_wrong_response_message()
            return
            
        # Send gender-appropriate text
        text = RECEIVE_OK_TERMS
        if gender == FEMALE:
            text = RECEIVE_OK_TERMS_FEMALE
            
        await send_age_question(text)
    except Exception as e:
        logger.error(f"Error handling terms acceptance: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_none(callback_data: str) -> None:
    """
    Handle new conversation initialization or reset.
    
    Deletes any existing conversation data and starts a new conversation.
    
    Args:
        callback_data: Source of the request ("new", "from_what", etc.)
    """
    logger.info(f"Processing conversation reset from {username}, source: {callback_data}")
    
    try:
        # Try to delete existing conversation, but don't fail if it doesn't exist
        delete_conversation(username)
        logger.info(f"Cleaned up existing conversation for {username}")
    except Exception as e:
        logger.warning(f"Error cleaning up conversation for {username}: {e}")
    
    try:
        await start_conversation()
        logger.info(f"Started new conversation for {username}")
    except Exception as e:
        logger.error(f"Failed to start new conversation for {username}: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_calib_video_callback(callback_data: str) -> None:
    """
    Handle VIP user calibration video callback.
    
    Sets state for calibration video upload and sends instructions.
    
    Args:
        callback_data: Callback data (VIP_USER_CALIB)
    """
    logger.info(f"Processing calibration video request from VIP user {username}")
    
    try:
        success = update_chat_db({STATE: VIP_USER_CALIB}, username)
        if success:
            await send_vip_user_calib_instructions()
        else:
            logger.error(f"Failed to update state for VIP user {username}")
            await send_wrong_response_message()
    except Exception as e:
        logger.error(f"Error handling calibration video callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_sentence_video_callback(callback_data: str) -> None:
    """
    Handle VIP user sentence video callback.
    
    Sets state for sentence input and sends appropriate instructions.
    
    Args:
        callback_data: Callback data (VIP_USER_SENTENCE)
    """
    logger.info(f"Processing sentence video request from VIP user {username}")
    
    try:
        success = update_chat_db({STATE: VIP_USER_GET_SENTENCE}, username)
        if success:
            await send_vip_user_sentence_instructions()
        else:
            logger.error(f"Failed to update state for VIP user {username}")
            await send_wrong_response_message()
    except Exception as e:
        logger.error(f"Error handling sentence video callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_what_callback(callback_data: str) -> None:
    """
    Handle "what" callback - shows current state context.
    
    Sends appropriate message/menu based on current conversation state.
    
    Args:
        callback_data: Callback data (WHAT)
    """
    logger.info(f"Processing 'what' request from {username}, current state: {state}")
    
    try:
        bot = Bot(TOKEN)
        await bot.send_message(chat_id, WHAT_TEXT)
        
        # Define state-to-action mapping
        state_actions = {
            VIP_USER_MENU: send_vip_user_menu,
            PLACE: send_place_question,
            LIGHTING_COLOR: send_lighting_color_question,
            LIGHTING_INTENSITY: send_lighting_intensity_question,
            VIP_USER_GET_SENTENCE: send_vip_user_sentence_instructions,
            VIP_USER_SENTENCE: send_vip_user_sentence_video_instructions,
            VIP_USER_CALIB: send_vip_user_calib_instructions,
            INIT: send_briefing_menu,
            GENDER: send_gender_question,
            AGE: send_age_question,
            ACCENT: send_accent_question,
            FIRST_VIDEO: send_first_video_instructions,
            SECOND_VIDEO: send_second_video_instructions,
            NTH_VIDEO: send_second_video_instructions,
            LAST_CHOICE: send_nth_video_menu,
            None: handle_none
        }

        action = state_actions.get(state)
        if action:
            # Some actions need additional parameters
            if state in [SECOND_VIDEO, NTH_VIDEO, VIP_USER_SENTENCE]:
                sentence = get_from_chat_db(SENTENCE, username)
                if sentence:
                    await action(sentence)
                else:
                    logger.warning(f"No sentence found for user {username} in state {state}")
                    await handle_none("missing_sentence")
            elif state is None:
                await handle_none("from_what")
            else:
                await action()
        else:
            logger.warning(f"No action found for state: {state}")
            await handle_none("unknown_state")
            
    except Exception as e:
        logger.error(f"Error handling 'what' callback: {e}", exc_info=True)
        await send_wrong_response_message()


async def handle_callback_query(callback_data: str) -> None:
    """
    Main callback query handler - routes callback data to appropriate handlers.
    
    This function maps callback data to specific handler functions and
    executes the appropriate action based on the user's selection.
    
    Args:
        callback_data: The callback data from the Telegram inline keyboard
    """
    logger.info(f"Processing callback query from {username}: {callback_data}")

    # Define callback-to-handler mapping
    callback_actions = {
        VIP_USER_CALIB: handle_calib_video_callback,
        VIP_USER_SENTENCE: handle_sentence_video_callback,
        MALE: handle_gender_callback,
        FEMALE: handle_gender_callback,
        BRIEF1: handle_brief_callback,
        LETSTART: handle_letstart_callback,
        OK_TERMS: handle_ok_terms_callback,
        OK_TERMS_FEMALE: handle_ok_terms_callback,
        ACCENT1: handle_accent_callback,
        ACCENT2: handle_accent_callback,
        ACCENT3: handle_accent_callback,
        ACCENT4: handle_accent_callback,
        ACCENT5: handle_accent_callback,
        ACCENT6: handle_accent_callback,
        ACCENT7: handle_accent_callback,
        OK_NTH: handle_send_video_callback,
        IM_DONE: handle_done_callback,
        QUIT: handle_quit_callback,
        WHAT: handle_what_callback,
        None: handle_none,
        RESET: handle_none,
    }

    action = callback_actions.get(callback_data)
    if action:
        try:
            await action(callback_data)
            logger.info(f"Successfully processed callback: {callback_data}")
        except Exception as e:
            logger.error(f"Error in callback handler for {callback_data}: {e}", exc_info=True)
            await send_wrong_response_message()
    else:
        logger.warning(f"No handler found for callback data: {callback_data}")
        await send_wrong_response_message()
