from telegram import Bot

from lambda_function import state, username, gender, start_conversation, gender_suitble_text, \
    chat_id
from sqs_service import get_next_sentence_from_queue
from db_service import get_from_chat_db, update_chat_db, delete_conversation
from texts import CONFIG, GENDER, TERMS, INIT, VIP_USER_MENU, VIP_USER_CALIB, VIP_USER_SENTENCE, BRIEF, AGE, ACCENT, \
    FIRST_VIDEO, VIP_USER_GET_SENTENCE, SECOND_VIDEO, LAST_CHOICE, NTH_VIDEO, STATE, SENTENCE, LIGHTING_COLOR, \
    LIGHTING_INTENSITY, PLACE, MALE, FEMALE, ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, ACCENT6, ACCENT7, OK_TERMS, \
    OK_NTH, IM_DONE, OK_TERMS_FEMALE, QUIT, WHAT, RESET, BRIEF1, LETSTART, ADMIN, TOKEN, RECEIVE_OK_TERMS, \
    RECEIVE_OK_TERMS_FEMALE, WHAT_TEXT
from send_options import send_config_message, send_success_message, send_config_menu, send_briefing_menu, \
    send_accent_specific, send_first_video_instructions, send_nth_video_instructions, send_goodbye, send_brief, \
    send_terms, send_age_question, send_vip_user_calib_instructions, send_vip_user_menu, send_place_question, \
    send_lighting_color_question, send_lighting_intensity_question, send_vip_user_sentence_instructions, \
    send_vip_user_sentence_video_instructions, send_gender_question, send_accent_question, \
    send_second_video_instructions, send_nth_video_menu, send_wrong_response_message


async def handle_quit_callback(callback_data):
    if state == CONFIG and username == ADMIN:
        delete_conversation()
        await send_config_message()
    else:
        await send_success_message()
        await send_config_menu()


async def handle_gender_callback(callback_data):
    data_values = {
        GENDER: callback_data,
        STATE: BRIEF,
    }
    update_chat_db(data_values)
    await send_briefing_menu()


async def handle_accent_callback(callback_data):
    if callback_data == ACCENT2:
        await send_accent_specific()
    else:
        data_values = {
            ACCENT: callback_data,
            STATE: FIRST_VIDEO,
        }
        update_chat_db(data_values)

        await send_first_video_instructions()


async def handle_send_video_callback(callback_data):
    sentence = get_next_sentence_from_queue()
    print('THE TEXT IS: ' + str(sentence))
    await send_nth_video_instructions(sentence)

    update_chat_db({STATE: NTH_VIDEO, SENTENCE: sentence})


async def handle_done_callback(callback_data):
    delete_conversation()
    await send_goodbye()


async def handle_brief_callback(callback_data):
    await send_brief()


async def handle_letstart_callback(callback_data):
    data_values = {
        STATE: TERMS
    }
    update_chat_db(data_values)
    await send_terms()


async def handle_ok_terms_callback(callback_data):
    update_chat_db({STATE: AGE})
    text = RECEIVE_OK_TERMS
    if gender == FEMALE:
        text = RECEIVE_OK_TERMS_FEMALE
    await send_age_question(text)


async def handle_none(callback_data):
    try:
        delete_conversation()
    except Exception as e:
        print(e)
    finally:
        await start_conversation()


async def handle_calib_video_callback(callback_data):
    update_chat_db({STATE: VIP_USER_CALIB})
    await send_vip_user_calib_instructions()


async def handle_sentence_video_callback(callback_data):
    update_chat_db({STATE: VIP_USER_SENTENCE})
    await send_age_question(gender_suitble_text(RECEIVE_OK_TERMS))


async def handle_what_callback(callback_data):
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, WHAT_TEXT)
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
        if state in [SECOND_VIDEO, NTH_VIDEO, VIP_USER_SENTENCE]:
            await action(get_from_chat_db(SENTENCE))
        elif state is None:
            await handle_none("from_what")
        else:
            await action()
    else:
        await handle_none("the_hell?")


async def handle_callback_query(callback_data):
    print(f"Callback query: [{callback_data}]")

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
        await action(callback_data)

    else:
        await send_wrong_response_message()
