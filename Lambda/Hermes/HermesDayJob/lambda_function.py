import json

import requests
import boto3
from datetime import datetime

# States
CONFIG = 'config'
NOAM_CALIB = "קליברציה"
NOAM_SENTENCE = "משפט"
AGE = 'age'
ACCENT = 'accent'
FIRST_VIDEO = 'first_video'
SECOND_VIDEO = 'second_video'
LAST_CHOICE = 'last_choice'
NTH_VIDEO = 'nth_video'

# Atributes
STATE = 'state'
USER_NAME = 'user_name'
SENTENCE = 'sentence'
SESSION_ID = 'session_id'
LIGHTING_COLOR = 'LIGHTING_COLOR'
LIGHTING_INTENSITY = 'LIGHTING_INTENSITY'
PLACE = 'place'

# Resorces
NOAM = 'Noam'
ADMIN = 'Zebambi'
CHAT_TABLE = "ChatDB"
TEXT_TABLE = "TextDB"
GUEST = 'Royshefy'
TOKEN = '5900828587:AAE9eVD3NCMQv9mhEx_mLUSX9PzVO9Ih2jE'
S3_BUCKET_NAME = 'lipsync'

# Atributes
FILE_ID = 'file_id'
GENDER = 'gender'
# globals
chat_id = None
accent = None
username = None
state = None
gender = None
session_id = None
video_file_id = None
sentence = None
place = None
intensity = None
color = None
response = None

db_source = boto3.resource('dynamodb')
chat_table = db_source.Table(CHAT_TABLE)
s3_client = boto3.client("s3")


def delete_conversation():
    print(f"Deleting user_name: {username} from ChatDB")
    chat_table.delete_item(Key={USER_NAME: username})


def get_file_url(file_id):
    # Call Telegram Bot API's getFile method to retrieve the file's URL
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}")
    response_json = response.json()
    file_path = response_json['result']['file_path']
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    return file_url


def run_get_loop(table, key, max_attempts=2):
    i = 0
    while i < max_attempts:
        response1 = table.get_item(Key=key)
        if response1.get('Item'):
            item = response1['Item']
            print("Retrieved item:", item)
            return item  # Exit the loop and return the retrieved item
        i += 1

    print(f"Failed to retrieve item after {max_attempts} attempts")
    return None


def handle_noam_calib_video():
    s3_key = f'Noam/{place}/{intensity}/{color}/calibration.mp4'
    s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)
    delete_conversation()


def handle_noam_sentence_video():
    s3_key = f'Noam/{place}/{intensity}/{color}/{sentence}.mp4'
    s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)
    delete_conversation()


def handle_config_video():
    global session_id

    now = datetime.now()
    session_id = now.strftime("%m/%d/%H:%M")
    s3_key = f'Inputs/{session_id}/{video_file_id}.mp4'
    s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)


def handle_first_video():
    s3_key = f'Sessions/{accent}/{session_id}/{username}/calibration.mp4'
    s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)


def handle_second_video():
    s3_key = f'Sessions/{accent}/{session_id}/{username}/calibration.mp4'
    s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)


def upload_video():
    if response.status_code == 200:
        state_actions = {

            FIRST_VIDEO: handle_first_video,
            SECOND_VIDEO: handle_second_video,
            NTH_VIDEO: handle_second_video,
            CONFIG: handle_config_video,
            NOAM_SENTENCE: handle_noam_sentence_video,
            NOAM_CALIB: handle_noam_calib_video,
        }

        action = state_actions.get(state)
        if action:
            action()
    else:
        return {
            'statusCode': 500,
            'body': 'Error while getting video from telegram servers',
        }


def lambda_handler(event, context):
    print("#################### New event ###########################")
    try:

        global username
        global chat_id
        global username
        global state
        global gender
        global session_id
        global video_file_id
        global sentence
        global accent
        global place
        global color
        global intensity
        global response

        # get data from event:
        print(event)
        print(type(event))

        username = event.get(USER_NAME)
        print(username)
        video_file_id = event.get(FILE_ID)
        video_url = get_file_url(video_file_id)
        state = event.get(STATE)

        # get data from Chat table:
        conv = run_get_loop(chat_table, {USER_NAME: username})
        print(conv)
        print(type(conv))
        if username == NOAM:
            place = conv.get(PLACE)
            intensity = conv.get(LIGHTING_INTENSITY)
            color = conv.get(LIGHTING_COLOR)
        else:
            accent = conv.get(ACCENT)
            session_id = conv.get(SESSION_ID)
        sentence = conv.get(SENTENCE)

        print(f"File ID: {video_file_id}")
        print(f"File URL: {video_url}")
        response = requests.get(video_url, stream=True)
        upload_video()

    except Exception as e:
        print(e)
    return {
        'statusCode': 200
    }
