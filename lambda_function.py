import asyncio
import json
import time
import requests
from datetime import datetime

from db_service import db_source, run_get_loop
from handle_callback import handle_callback_query
from handle_message import handle_message
from handle_video import handle_video
from send_options import send_initial_vip_user, send_place_question, \
    send_gender_question, \
    send_wrong_response_message
from texts import GENDER, AGE, ACCENT, STATE, USER_NAME, SESSION_ID, LIGHTING_COLOR, LIGHTING_INTENSITY, PLACE, TTL, MALE, \
    VIP_USER, CHAT_TABLE, TOKEN

# globals
chat_id = None
username = None
state = None
gender = None


def lambda_handler(event, context):
    print("#################### New event ###########################")
    try:
        body = json.loads(event['body'])
        asyncio.run(process(body))

    except Exception as e:
        print(e)
    return {
        'statusCode': 200
    }


def get_user_info(body):
    print("Collecting chat_id and user_name from event['body']")
    if 'message' in body:
        _chat_id = body.get('message').get('chat').get('id')
        _username = body.get('message').get('from').get('username')
    elif 'callback_query' in body:
        _chat_id = body.get('callback_query').get('message').get('chat').get('id')
        _username = body.get('callback_query').get('from').get('username')
    else:
        raise Exception
    return _chat_id, _username


async def process(body):
    global chat_id
    global username
    global state
    global gender

    chat_id, username = get_user_info(body)
    if not chat_id:
        return {'statusCode': 400}
    if not username:
        username = str(chat_id)

    chat_table = db_source.Table(CHAT_TABLE)
    conversation = run_get_loop(chat_table, {USER_NAME: username})
    if conversation:
        state = conversation.get(STATE)
        if username != VIP_USER:
            gender = conversation.get(GENDER)

    print(f"Woke up in state: {state}")
    print(f"Coming from user_name: {username}")
    bot = Bot(TOKEN)
    await bot.send_chat_action(chat_id, 'typing')

    if 'message' in body:

        message = body['message']
        text = message.get('text')
        video_file_id = message.get('video').get('file_id') if 'video' in message else None

        if text:
            await handle_message(text, username, state)

        elif video_file_id:
            await handle_video(video_file_id, state)

    elif 'callback_query' in body:
        callback_query = body['callback_query']
        data = callback_query['data']
        await handle_callback_query(data)

    else:
        print("no text or callback query were given")
        await send_wrong_response_message()


def get_file_url(file_id):
    # Call Telegram Bot API's getFile method to retrieve the file's URL
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}")
    response_json = response.json()
    file_path = response_json['result']['file_path']
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    return file_url


async def start_conversation():
    print(f"creating a new chat for {username} at the Data Base")
    now = datetime.now()
    session_id = now.strftime("%m/%d/%H:%M")
    chat_table = db_source.Table(CHAT_TABLE)

    if username == VIP_USER:
        attribute_updates = {STATE: PLACE, GENDER: MALE, AGE: '51', ACCENT: 'none',
                             LIGHTING_INTENSITY: '0', LIGHTING_COLOR: 'none'}
        await send_initial_vip_user()
        await send_place_question()
    else:
        current_time = int(time.time())
        expiration_time = current_time + (10 * 60)
        attribute_updates = {STATE: GENDER, GENDER: 'none', AGE: '0', ACCENT: 'none',
                             SESSION_ID: session_id, TTL: expiration_time}
        await send_gender_question()

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
        print("Updated attributes:", updated_attributes)
    else:
        print("Could not set usernames chat data:", username)


def gender_suitble_text(RECEIVE_OK_TERMS):
    pass
