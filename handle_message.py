from db_service import update_chat_db
from handle_callback import handle_none
from texts import CONFIG, VIP_USER_MENU, VIP_USER_SENTENCE, AGE, ACCENT, VIP_USER_GET_SENTENCE, STATE, SENTENCE, \
    LIGHTING_COLOR, LIGHTING_INTENSITY, PLACE, ADMIN
from send_options import send_config_message, send_config_menu, send_accent_question, send_default_response, \
    send_lighting_intensity_question, send_lighting_color_question, send_vip_user_menu, \
    send_vip_user_sentence_video_instructions, send_wrong_response_message


async def handle_message(text_message, username, state):
    print(f"Text message: {text_message}")

    if text_message.lower().startswith(CONFIG.lower()) and username == ADMIN:

        update_chat_db({STATE: CONFIG})
        await send_config_message()
        await send_config_menu()

    elif state is None or text_message == "חדש":
        await handle_none("new")

    elif state == AGE:
        print(f"AGE input: {str(text_message)}")
        if text_message.isdigit():
            update_chat_db({AGE: int(text_message), STATE: ACCENT})
            await send_accent_question()
        else:
            print("User entered invalid characters for AGE field")
            await send_default_response()

    elif state == PLACE:
        update_chat_db({PLACE: text_message, STATE: LIGHTING_INTENSITY})
        await send_lighting_intensity_question()

    elif state == LIGHTING_INTENSITY:
        if text_message.isdigit():
            update_chat_db({LIGHTING_INTENSITY: text_message, STATE: LIGHTING_COLOR})
            await send_lighting_color_question()
        else:
            print("User entered invalid characters for AGE field")
            await send_default_response()

    elif state == LIGHTING_COLOR:
        update_chat_db({LIGHTING_COLOR: text_message, STATE: VIP_USER_MENU})
        await send_vip_user_menu()

    elif state == VIP_USER_GET_SENTENCE:
        update_chat_db({SENTENCE: text_message, STATE: VIP_USER_SENTENCE})
        await send_vip_user_sentence_video_instructions(text_message)
    else:
        print("User sent a wrong message type")
        await send_wrong_response_message()
