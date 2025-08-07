from handle_callback import handle_none
from sqs_service import get_first_sentence_from_queue
from lambda_service import invoke_second_lambda
from db_service import update_chat_db
from send_options import send_wrong_response_message, send_vip_user_goodbye, send_success_message, send_config_menu, \
    send_nth_video_menu, send_second_video_instructions
from texts import FIRST_VIDEO, SECOND_VIDEO, NTH_VIDEO, CONFIG, VIP_USER_SENTENCE, VIP_USER_CALIB, STATE, LAST_CHOICE


async def handle_video(video_file_id, username, state):
    print(f"Incoming video at state: {state}")

    state_actions = {

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
        await action(video_file_id, state, username)

    else:
        await send_wrong_response_message()


async def handle_vip_user_video(video_file_id, state, username):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters, state)
    await send_vip_user_goodbye()


async def handle_config_video(video_file_id, state, username):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters, state)
    await send_success_message()
    await send_config_menu()


async def handle_second_video(video_file_id, state, username):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters, state)
    update_chat_db({STATE: LAST_CHOICE})
    await send_nth_video_menu()


async def handle_first_video(video_file_id, state, username):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters, state)
    update_chat_db({STATE: SECOND_VIDEO})
    sentence = get_first_sentence_from_queue()
    print('THE TEXT IS: ' + str(sentence))
    await send_second_video_instructions(sentence)
