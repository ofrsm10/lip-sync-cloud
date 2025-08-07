import asyncio
import json
import time
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import boto3
from telegram import Bot
from datetime import datetime

# States
CONFIG = 'config'
GENDER = 'gender'
TERMS = 'terms'
INIT = 'init'
VIP_USER_MENU = 'VIP_USER_MENU'
VIP_USER_CALIB = "קליברציה"
VIP_USER_SENTENCE = "משפט"
BRIEF = 'briefing'
AGE = 'age'
ACCENT = 'accent'
RULES = 'rules'
FIRST_VIDEO = 'first_video'
GET_SENTENCE = 'get sentence'
VIP_USER_GET_SENTENCE = 'VIP_USER_GET_SENTENCE'
SECOND_VIDEO = 'second_video'
LAST_CHOICE = 'last_choice'
NTH_VIDEO = 'nth_video'
CURIOUS = 'corious'

# Attributes
STATE = 'state'
USER_NAME = 'user_name'
SENTENCE = 'sentence'
SESSION_ID = 'session_id'
LIGHTING_COLOR = 'LIGHTING_COLOR'
LIGHTING_INTENSITY = 'LIGHTING_INTENSITY'
PLACE = 'place'
TTL = 'ttl'

# Answers
MALE = "זכר"
FEMALE = "נקבה"
ACCENT1 = 'לא'
ACCENT2 = 'כן'
ACCENT3 = 'צרפתי'
ACCENT4 = 'סלאבי'
ACCENT5 = 'אמריקאי'
ACCENT6 = 'לטיני'
ACCENT7 = 'אחר'
OK_TERMS = "אני מאשר"
OK_NTH = "יאללה, למה לא"
IM_DONE = "בהזדמנות אחרת"
OK_TERMS_FEMALE = "אני מאשרת"
QUIT = 'quit'
WHAT = "רגע, איפה היינו?"
RESET = "בוא נתחיל את השיחה מחדש"
BRIEF1 = "כן בקצרה, מה נעשה עכשיו?"
LETSTART = "לא, בוא נתחיל"

# Resources
VIP_USER = 'Noam'
ADMIN = 'Zebambi'
CHAT_TABLE = "ChatDB"
TEXT_TABLE = "TextDB"
GUEST = 'Royshefy'
TOKEN = '5900828587:AAE9eVD3NCMQv9mhEx_mLUSX9PzVO9Ih2jE'
S3_BUCKET_NAME = 'lipsync'
WEBHOOK_URL = 'https://wjxuhw70qk.execute-api.eu-north-1.amazonaws.com/LambdaTelegramBot'
QUEUE_URL = 'https://sqs.eu-north-1.amazonaws.com/018857904869/sentence_queue'
DEMO1_VIDEO_ID = 'BAACAgQAAxkBAAIMSWSIRhdtrXCHEUCMH2Py8I6_q9j3AAK9EwACkApAUHbMxGUWd6bsLwQ'
DEMO2_VIDEO_ID = 'BAACAgQAAxkBAAIMamSIR_-YIoh2BhEkfR-70qwxiptzAALIEwACkApAUJgbgCttnWbGLwQ'

# VIP_USER'S CONVERSATION:
INITIAL_VIP_USER = "הו שלום לך אדוני!\n\n" \
                   "ברוך בואך, " \
                   "כאן אלפרד לשירותך \U0001F916\n"
ASK_PLACE = "איפה אתה עומד לצלם כרגע?"
ASK_COLOR = "מה הצבע הדומיננטי של התאורה סביבך?"
ASK_INTENSITY = "מאחד עד עשר, כמה מואר סביבך? (עשר זה אור יום)"
ASK_STEP = "איזה סרטון אתה רוצה לשלוח?"
CALIB_INSTRUCTIONS = "תשלח סרטון שלך מוציא לשון במשך שניה, ואז מחייך עם שיניים במשך שניה נוספת"
GET_SENTENCE_INSTRUCTIONS = f"תשלח בהודעה, את המשפט שאתה עומד להקליט"
RECEIVED_VIDEO = 'קיבלתי!\n אם אתה רוצה לשלוח עוד סרטונים אני פה, רק תשלח הודעה :)'

# public STORYLINE:


ASK_GENDER = "מיד נתחיל\n\nסמנ/י את המין שלך\n\n"

OFFER_BRIEF = "*ברוך הבא ל-Project lipSync*\n\n" \
              "אני אלפרד \U0001F916\nעבדו הנאמן של עופר ומנהל הדאטה של הפרויקט.\n\n" \
              "קודם כל, תודה ענקית שבאת לתרום מזמנך, זה לא מובן מאליו.\n" \
              "בתקווה, נצליח לקחת את המילים שלך ולהעניק אותן חזרה לאלו שאיבדו אותן.\n" \
              "התרומה שלך יקרה מפז!\n\n" \
              "האם תרצה לשמוע קצת על התהליך? "

OFFER_BRIEF_FEMALE = "*ברוכה הבאה ל-Project lipSync*\n\n" \
                     "אני אלפרד \U0001F916\nעבדו הנאמן של עופר ומנהל הדאטה של הפרויקט.\n\n" \
                     "קודם כל, תודה ענקית שבאת לתרום מזמנך, זה לא מובן מאליו.\n" \
                     "בתקווה, נצליח לקחת את המילים שלך ולהעניק אותן חזרה לאלו שאיבדו אותן.\n" \
                     "התרומה שלך יקרה מפז!\n\n" \
                     "האם תרצי לשמוע קצת על התהליך?"

BRIEF_TEXT = "*אז מה הולך להיות לנו?*\n\n" \
             "קודם כל, נרגיע את הפאניקה- יש לנו רק 3 דקות יחד וזה נגמר. אני אשאל 2 שאלות, אתה תצלם 2 סרטונים וסיימנו!\n\n" \
             "*סרטון ראשון* נועד כדי ללמוד את הנתונים הוויזואלים שלך ולהתאים את המערכת אליהם.\n\n" \
             "*סרטון שני* נועד כדי להרחיב את אוצר המילים של המערכת.\n\n" \
             "וזהו! אחרי זה תוכל להישאר ולהמשיך לתרום כמה שרק בא לך.\n\n" \
             "*מוכן לזה?*"

BRIEF_TEXT_FEMALE = "*אז מה הולך להיות לנו?*\n\n" \
                    "קודם כל, נרגיע את הפאניקה- יש לנו רק 3 דקות יחד וזה נגמר. אני אשאל 2 שאלות, את תצלמי 2 סרטונים וסיימנו!\n\n" \
                    "*סרטון ראשון* נועד כדי ללמוד את הנתונים הוויזואלים שלך ולהתאים את המערכת אליהם.\n\n" \
                    "*סרטון שני* נועד כדי להרחיב את אוצר המילים של המערכת.\n\n" \
                    "וזהו! אחרי זה תוכלי להישאר ולהמשיך לתרום כמה שרק בא לך.\n\n" \
                    "*מוכנה לזה?*"

TERMS_TEXT = "בלחיצה על הכפתור, אתה נותן לי את האישור להשתמש בסרטונים שאקבל ממך בשיחה זו, לטובת קריאת " \
             "שפתיים מוידאו."
TERMS_TEXT_FEMALE = "בלחיצה על הכפתור, את נותנת לי את האישור להשתמש בסרטונים שאקבל ממך בשיחה זו, לטובת קריאת " \
                    "שפתיים מוידאו."

RECEIVE_OK_TERMS = "נהדר! בוא נתחיל.\n" \
                   "מה הגיל שלך?"

RECEIVE_OK_TERMS_FEMALE = "נהדר! בואי נתחיל.\n" \
                          "מה הגיל שלך?"

ASK_ACCENT = "\n\nהאם אדוני מדבר עם מבטא זר?"
ASK_ACCENT_FEMALE = "\n\nהאם גברתי מדברת עם מבטא זר?"
ASK_ACCENT_SPECIFIC = "בחר את המבטא מתוך הרשימה"
ASK_ACCENT_SPECIFIC_FEMALE = "בחרי את המבטא מתוך הרשימה"

FIRST_VIDEO_TEXT1 = "השלב הבא ישמע קצת מוזר, אבל הוא *חיוני* להתאמת המערכת " \
                    "לאנשים בעלי מאפיינים ויזואלים שונים זה מזה. \n\nלמה? כי חלק מהמידע שאני שואב מהוידאו, טמון בצבעים של הלשון והשיניים שלך.\n\n"

FIRST_VIDEO_TEXT2 = "*סרטון ראשון*\n\n" \
                    "*נקה* את העדשה של מצלמת הסלפי בעזרת בד.\n\n" \
                    "*הדלק תאורה חזקה,* עדיף אור לבן. \n\n" \
                    "*הקפד לא לזוז במהלך הצילום*, הבט ישר למצלמה והחזק את הפלפאון בגובה העיניים.\n\n" \
                    "*צלם מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                    "*הפעל את מצלמת הסלפי מתוך טלגרם,* לחץ על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                    "*צלם את עצמך* מוציא לשון במשך שניה ואז מחייך חיוך גדול עם שיניים במשך שניה נוספת. סגור את הפה בין הפעולות, בדיוק כמו בסרטון ששלחתי.\n\n" \
                    "*כשסיימת*, צפה בסרטון, וודא שעמדת בכללים, ושלח.\n\n"

FIRST_VIDEO_TEXT2_FEMALE = "*סרטון ראשון*\n\n" \
                           "*נקי* את העדשה של מצלמת הסלפי בעזרת בד.\n\n" \
                           "*הדליקי תאורה חזקה,* עדיף אור לבן. \n\n" \
                           "*הקפידי לא לזוז במהלך הצילום*, הביטי ישר למצלמה והחזיקי את הפלפאון בגובה העיניים.\n\n" \
                           "*צלמי מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                           "*הפעילי את מצלמת הסלפי מתוך טלגרם,* לחצי על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                           "*צלמי את עצמך* מוציאה לשון במשך במשך שניה ואז מחייכת חיוך גדול עם שיניים במשך שניה נוספת. סגרי את הפה בין הפעולות, בדיוק כמו בסרטון ששלחתי.\n\n" \
                           "*כשסיימת*, צפי בסרטון, וודאי שעמדת בכללים, ושלחי.\n\n"

ASK_NTH_VIDEO = 'יש! קיבלתי! \nאין עליך.. ' \
                'זהו, אתה משוחרר!\nאלא אם אתה מעוניין לעזור עוד טיפ טיפה..' \
                ' מממ מה אתה אומר? תרצה לתרום משפט נוסף?'
ASK_NTH_VIDEO_FEMALE = 'יש! קיבלתי! \n\nאין עליך..' \
                       'זהו, את משוחררת!\n אלא אם את מעוניינת לעזור עוד טיפ טיפה..' \
                       'מממ מה את אומרת? תרצי לתרום משפט נוסף?'

GOODBYE_TEXT = "בסדר גמור. לגמרי תרמת את חלקך.\n" \
               "תודה על כך. אתה מדהים, באמת!\n\n" \
               "אם סיימנו פה, אגש לבדוק את הסרטונים.. \nאולי אכין לעופר משהו לאכול, " \
               "הוא בדיוק צריך להגיע.. \n\nאדוני, היה תענוג. מוזמן לקפוץ בכל שעה! \U0001F916"
GOODBYE_TEXT_FEMALE = "בסדר גמור. לגמרי תרמת את חלקך.\n" \
                      "תודה על כך. את מדהימה, באמת!\n\n" \
                      "אם סיימנו פה, אגש לבדוק את הסרטונים.. \nאולי אכין לעופר משהו לאכול, " \
                      "הוא בדיוק צריך להגיע.. \n\nגבירתי, היה תענוג. מוזמנת לקפוץ בכל שעה! \U0001F916"

WRONG_ACTION_TEXT = "לא השלב לשלוח את זה..." \
                    "בבקשה שימ/י לב להנחיות ותפעל/י בהתאם"
WHAT_TEXT = "היינו פה.."
WRONG_REPLY_TEXT = "מצטער, עליך להיות מעל גיל 16 כדי לתרום.. אולי בעתיד!"
FAIL_DOWNLOAD_TEXT = "לא הצלחתי להוריד את הסרטון ששלחת, תוכל/י לשלוח שוב?"
HELP = "כדי להתחיל את השיחה מחדש, שלח/י את המילה ״חדש״\n\n"

# globals
chat_id = None
username = None
state = None
gender = None
db_source = boto3.resource('dynamodb')


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
            await handle_message(text)

        elif video_file_id:
            await handle_video(video_file_id)

    elif 'callback_query' in body:
        callback_query = body['callback_query']
        data = callback_query['data']
        await handle_callback_query(data)

    else:
        print("no text or callback query were given")
        await send_wrong_response_message()


def invoke_second_lambda(parameters):
    print("Downloading video with the help of second lambda")
    try:
        lambda_client = boto3.client('lambda')
        payload = {
            STATE: state,
            USER_NAME: parameters[0],
            "file_id": parameters[1]
        }
        payload_json = json.dumps(payload)

        params = {
            'FunctionName': 'HermesDayJob',
            'InvocationType': 'Event',  # Invoke asynchronously
            'Payload': payload_json,
        }
        lambda_client.invoke(**params)
        return {
            'statusCode': 200,
            'body': 'Second Lambda function triggered successfully',
        }
    except Exception as e:
        # Handle any errors that occurred during the invocation
        print('Error invoking second Lambda function:', str(e))
        return {
            'statusCode': 500,
            'body': 'Error invoking second Lambda function',
        }


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
        print("Could set usernames chat data:", username)


async def handle_video(video_file_id):
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
        await action(video_file_id)

    else:
        await send_wrong_response_message()


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


async def handle_message(text_message):
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


def get_first_sentence_from_queue():
    queue_url = QUEUE_URL
    sqs = boto3.client('sqs')

    # Receive messages from the queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        AttributeNames=['ApproximateReceiveCount']
    )

    # Check if any messages are received
    if 'Messages' in response:
        message = response['Messages'][0]
        sentence = message['Body']

        receive_count = int(message['Attributes']['ApproximateReceiveCount'])
        print(f"Processing sentence: {sentence}")
        print(f"Recieve Count: {receive_count}")
        if receive_count > 10:
            # Delete the message from the queue
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

        return sentence
    # No messages in the queue
    return None


def get_next_sentence_from_queue():
    queue_url = QUEUE_URL
    sqs = boto3.client('sqs')

    # Receive messages from the queue with a visibility timeout of 0
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    # Check if any messages are received
    if 'Messages' in response:
        message = response['Messages'][0]
        sentence = message['Body']

        # Process the sentence (your custom logic goes here)
        print(f"Processing sentence: {sentence}")

        # Delete the message from the queue
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        return sentence

    # No unreceived sentences in the queue
    return None


def get_from_chat_db(data):
    chat_table = db_source.Table(CHAT_TABLE)
    retrieved_item = run_get_loop(chat_table, {USER_NAME: username})
    if retrieved_item:
        return retrieved_item.get(data)
    else:
        return None


def update_chat_db(data_values):
    chat_table = db_source.Table(CHAT_TABLE)
    print("Updating attributes in ChatDB")

    i = 0
    while i < 5:
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
            print("Updated attributes:", updated_attributes)
            return True
        i += 1

    print(f"Failed to update attributes after 5 attempts")
    return False


def delete_conversation():
    chat_table = db_source.Table(CHAT_TABLE)
    print(f"Deleting user_name: {username} from ChatDB")
    response = chat_table.delete_item(Key={USER_NAME: username})
    # i = 0
    # while not response.get('ResponseMetadata').get('HTTPStatusCode') == 200 and i < 5:
    #     i += 1
    #     response = chat_table.delete_item(Key={USER_NAME: username})


def clear_bucket():
    s3_resource = boto3.resource('s3')
    s3_client = boto3.client("s3")

    objects = s3_client.list_objects(Bucket=S3_BUCKET_NAME)['Contents']
    for obj in objects:
        key = obj['Key']
        folder = key.split('/')[0]

        if folder in ['Sessions']:
            bucket = s3_resource.Bucket(S3_BUCKET_NAME)
            bucket.objects.filter(Prefix=key).delete()

    print('Folders deleted from the bucket:', S3_BUCKET_NAME)
    print('Folder cleanup completed.')
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key='Sessions/')


def clear_chat_table():
    chat_table = db_source.Table(CHAT_TABLE)
    response = chat_table.scan()
    items = response['Items']

    while 'LastEvaluatedKey' in response:
        response = chat_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    for item in items:
        if item[USER_NAME] == ADMIN:
            continue
        chat_table.delete_item(Key={USER_NAME: item[USER_NAME]})
        print(f"deleted item: {item[USER_NAME]}")


def run_get_loop(table, key, max_attempts=2):
    i = 0
    while i < max_attempts:
        response = table.get_item(Key=key)
        if response.get('Item'):
            item = response['Item']
            print("Retrieved item:", item)
            return item  # Exit the loop and return the retrieved item
        i += 1

    print(f"Failed to retrieve item after {max_attempts} attempts")
    return None


async def send_vip_user_sentence_video_instructions(sentence):
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, text=f"*צלם את עצמך חוזר אחרי המשפט: {sentence}*", parse_mode='Markdown')


async def send_vip_user_sentence_instructions():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, text=GET_SENTENCE_INSTRUCTIONS, parse_mode='Markdown')


async def send_vip_user_menu():
    button_option_a = InlineKeyboardButton(VIP_USER_CALIB, callback_data=VIP_USER_CALIB)
    button_option_b = InlineKeyboardButton(VIP_USER_SENTENCE, callback_data=VIP_USER_SENTENCE)

    keyboard = [[button_option_a],
                [button_option_b]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_STEP, reply_markup=reply_markup, parse_mode='Markdown')


async def send_initial_vip_user():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=INITIAL_VIP_USER, parse_mode='Markdown')


async def send_place_question():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_PLACE, parse_mode='Markdown')


async def send_vip_user_calib_instructions():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=CALIB_INSTRUCTIONS, parse_mode='Markdown')


async def send_lighting_color_question():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_COLOR, parse_mode='Markdown')


async def send_lighting_intensity_question():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=ASK_INTENSITY, parse_mode='Markdown')


async def send_vip_user_goodbye():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=RECEIVED_VIDEO, parse_mode='Markdown')


async def send_briefing_menu():
    print("Sending Brief menu..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(BRIEF1, callback_data=BRIEF1)
    # button_option_b = InlineKeyboardButton(BRIEF2, callback_data=BRIEF2)
    # button_option_c = InlineKeyboardButton("ספר לי עוד על הפרויקט", callback_data=BRIEF3)
    button_option_d = InlineKeyboardButton(LETSTART, callback_data=LETSTART)

    keyboard = [[button_option_a], [button_option_d]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = OFFER_BRIEF
    if gender == FEMALE:
        text = OFFER_BRIEF_FEMALE
    await bot.send_message(chat_id=chat_id,
                           text=text,
                           reply_markup=reply_markup, parse_mode='Markdown')


async def send_brief():
    print("Sending brief message..")
    bot = Bot(TOKEN)
    # button_option_a = InlineKeyboardButton(BRIEF1, callback_data=BRIEF1)
    # button_option_b = InlineKeyboardButton(BRIEF2, callback_data=BRIEF2)
    # button_option_c = InlineKeyboardButton("ספר לי עוד על הפרויקט", callback_data=BRIEF3)
    # button_option_d = InlineKeyboardButton(LETSTART, callback_data=LETSTART)
    button_option_e = InlineKeyboardButton('כן!', callback_data=LETSTART)

    keyboard = [[button_option_e]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if gender == MALE:
        await bot.send_message(chat_id=chat_id, text=BRIEF_TEXT, reply_markup=reply_markup,
                               parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=BRIEF_TEXT_FEMALE, reply_markup=reply_markup,
                               parse_mode='Markdown')


async def send_terms():
    print("Sending agreement message..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(OK_TERMS, callback_data=OK_TERMS)
    button_option_b = InlineKeyboardButton(OK_TERMS_FEMALE, callback_data=OK_TERMS)

    if gender == MALE:
        keyboard = [[button_option_a]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=TERMS_TEXT, reply_markup=reply_markup)
    else:
        keyboard = [[button_option_b]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=TERMS_TEXT_FEMALE, reply_markup=reply_markup)


async def send_gender_question():
    print("Sending gender question..")
    bot = Bot(TOKEN)
    text_message = ASK_GENDER
    button_option_a = InlineKeyboardButton(MALE, callback_data=MALE)
    button_option_b = InlineKeyboardButton(FEMALE, callback_data=FEMALE)
    keyboard = [[button_option_a], [button_option_b]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text_message, reply_markup=reply_markup, parse_mode='Markdown')


async def send_age_question(text):
    print("Sending age question..")
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def send_pdf():
    print("Sending email question..")
    bot = Bot(TOKEN)
    text = 'איזה כיף!\n הנה קובץ אשר סוקר את הפרויקט. במידה ויש לך שאלות נוספות, את מוזמן לפנות לעופר :)'
    if gender == FEMALE:
        text = 'איזה כיף!\n ת הנה קובץ אשר סוקר את הפרויקט.  במידה ויש לך שאלות נוספות, את מוזמנת לפנות לעופר :)'

    await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def send_accent_question():
    print("Sending accent question..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(ACCENT1, callback_data=ACCENT1)
    button_option_b = InlineKeyboardButton(ACCENT2, callback_data=ACCENT2)

    keyboard = [[button_option_a],
                [button_option_b]]
    text = ASK_ACCENT
    if gender == FEMALE:
        text = ASK_ACCENT_FEMALE
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='Markdown')


async def send_accent_specific():
    print("Sending accent specific..")
    bot = Bot(TOKEN)
    button_option_a = InlineKeyboardButton(ACCENT3, callback_data=ACCENT3)
    button_option_b = InlineKeyboardButton(ACCENT4, callback_data=ACCENT4)
    button_option_c = InlineKeyboardButton(ACCENT5, callback_data=ACCENT5)
    button_option_d = InlineKeyboardButton(ACCENT6, callback_data=ACCENT6)
    button_option_e = InlineKeyboardButton(ACCENT7, callback_data=ACCENT7)

    keyboard = [[button_option_a],
                [button_option_b],
                [button_option_c],
                [button_option_d],
                [button_option_e]]
    text = ASK_ACCENT_SPECIFIC
    if gender == FEMALE:
        text = ASK_ACCENT_SPECIFIC_FEMALE
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='Markdown')


async def send_first_video_instructions():
    print("Sending instructions for calibration video..")
    bot = Bot(TOKEN)

    url = get_file_url(DEMO1_VIDEO_ID)
    response = requests.get(url, stream=True)

    # await bot.send_message(chat_id=chat_id, text=FIRST_VIDEO_TEXT1, parse_mode='Markdown')
    if gender == MALE:
        await bot.send_message(chat_id=chat_id, text=FIRST_VIDEO_TEXT2, parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=FIRST_VIDEO_TEXT2_FEMALE, parse_mode='Markdown')
    await bot.send_video(chat_id=chat_id, video=response.raw)


async def send_second_video_instructions(sentence):
    print("Sending instructions for video..")
    bot = Bot(TOKEN)

    text_message = "קיבלתי!\nהו וואו.. איזה חיוך!\n" \
                   "אוקיי, כדור הארץ לאלפרד. \U0001F916\n\n\n" \
                   "*סרטון שני*\n\n" \
                   "*הקפד על דיקציה* מודגשת אך טבעית.\n\n" \
                   "*קח הפסקות ברורות* בין המילים, סגור את הפה לחלוטין כחצי שניה.\n\n" \
                   "*לא לזוז*, הבט ישר למצלמה והחזק את הפלפאון בגובה העיניים.\n\n" \
                   "*צלם מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                   "*הפעל את מצלמת הסלפי מתוך טלגרם,* לחץ על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                   "צלם את עצמך אומר את המשפט: " \
                   f"*{sentence}*\n\n" \
                   "*כשסיימת*, צפה בסרטון, וודא שעמדת בכללים בדיוק כמו בסרטון ששלחתי, ושלח!"

    if gender == FEMALE:
        text_message = "קיבלתי!\nהו וואו.. איזה חיוך!\n" \
                       "אוקיי, כדור הארץ לאלפרד. \U0001F916\n\n\n" \
                       "*סרטון שני*\n\n" \
                       "*הקפידי על דיקציה* מודגשת אך טבעית.\n\n" \
                       "*קחי הפסקות ברורות* בין המילים, סגרי את הפה לחלוטין כחצי שניה.\n\n" \
                       "*לא לזוז,* הביטי ישר למצלמה והחזיקי את הפלפאון בגובה העיניים.\n\n" \
                       "*צלמי מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                       "*הפעילי את מצלמת הסלפי מתוך טלגרם,* לחצי על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                       "צלמי את עצמך אומרת את המשפט: " \
                       f"*{sentence}*\n\n" \
                       "*כשסיימת,* צפי בסרטון, וודאי שעמדת בכללים בדיוק כמו בסרטון ששלחתי, ושלחי!"

    url = get_file_url(DEMO2_VIDEO_ID)
    response = requests.get(url, stream=True)
    await bot.send_message(chat_id=chat_id, text=text_message, parse_mode='Markdown')
    await bot.send_video(chat_id=chat_id, video=response.raw)


async def send_nth_video_instructions(sentence):
    print("Sending instructions for video..")
    bot = Bot(TOKEN)

    text_message = "יש! תודה!\n אוקיי, רק תזכורת לגבי הכללים: \n\n" \
                   "*דיקציה מודגשת* אך טבעית.\n\n" \
                   "*לקחת הפסקות ברורות* בין המילים, לסגור את הפה לחלוטין כחצי שניה.\n\n" \
                   "*לא לזוז,* הבט ישר למצלמה והחזק את הפלפאון בגובה העיניים.\n\n" \
                   "*צלם מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                   "*הפעל את מצלמת הסלפי מתוך טלגרם,* לחץ על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                   "צלם את עצמך אומר את המשפט: " \
                   f"*{sentence}*\n\n" \
                   "*כשסיימת,* צפה בסרטון, וודא שעמדת בכללים, ושלח."

    if gender == FEMALE:
        text_message = "יש! תודה!\n אוקיי, רק תזכורת לגבי הכללים: \n\n" \
                       "*דיקציה מודגשת* אך טבעית.\n\n" \
                       "*לקחת הפסקות ברורות* בין המילים, לסגור את הפה לחלוטין כחצי שניה.\n\n" \
                       "*לא לזוז,* הביטי ישר למצלמה והחזיקי את הפלפאון בגובה העיניים.\n\n" \
                       "*צלמי מקרוב,* הפנים שלך צריכות לכסות את רוב המסך.\n\n" \
                       "*הפעילי את מצלמת הסלפי מתוך טלגרם,* לחצי על כפתור השיתוף ואז על החלון שמראה תמונה חיה.  \n\n" \
                       "צלמי את עצמך אומרת את המשפט: " \
                       f"*{sentence}*\n\n" \
                       "*כשסיימת,* צפי בסרטון, וודאי שעמדת בכללים, ושלחי."

    await bot.send_message(chat_id=chat_id, text=text_message, parse_mode='Markdown')


async def send_nth_video_menu():
    print("Sending n'th video menu..")
    bot = Bot(TOKEN)

    keyboard = [[InlineKeyboardButton(OK_NTH, callback_data=OK_NTH)],
                [InlineKeyboardButton(IM_DONE, callback_data=IM_DONE)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if gender == MALE:
        await bot.send_message(chat_id=chat_id, text=ASK_NTH_VIDEO, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=ASK_NTH_VIDEO_FEMALE, reply_markup=reply_markup,
                               parse_mode='Markdown')


async def send_config_message():
    print("Sending config message..")
    bot = Bot(TOKEN)
    text_message1 = "Hi Admin, it's good to see you"
    text_message2 = "Exiting Configuration"
    message = text_message1 if state == CONFIG else text_message2
    await bot.send_message(chat_id, message)


async def send_config_menu():
    print("Sending config menu..")
    bot = Bot(TOKEN)

    keyboard = [[InlineKeyboardButton("Clear Chat DB", callback_data="clear_chat_table")],
                [InlineKeyboardButton("Reset Text DB", callback_data="reset_sentence_table")],
                [InlineKeyboardButton("Clear S3", callback_data="clear_bucket")],
                [InlineKeyboardButton("Quit config", callback_data=QUIT)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text_message = "What action would you like to take?"

    await bot.send_message(chat_id=chat_id, text=text_message, reply_markup=reply_markup)


async def send_goodbye():
    print("Sending success message..")
    bot = Bot(TOKEN)

    if gender == MALE:
        button_option_a = InlineKeyboardButton("התחל שיחה חדשה", callback_data=RESET)
        keyboard = [[button_option_a]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=GOODBYE_TEXT,
                               reply_markup=reply_markup, parse_mode='Markdown')
    else:
        button_option_a = InlineKeyboardButton("התחילי שיחה חדשה", callback_data=RESET)
        keyboard = [[button_option_a]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=GOODBYE_TEXT_FEMALE,
                               reply_markup=reply_markup, parse_mode='Markdown')


async def send_success_message():
    print("Sending success message..")
    bot = Bot(TOKEN)
    text_message = "Done!"

    await bot.send_message(chat_id=chat_id, text=text_message)


async def send_wrong_response_message():
    bot = Bot(TOKEN)

    button_option_a = InlineKeyboardButton(WHAT, callback_data=WHAT)
    button_option_b = InlineKeyboardButton(RESET, callback_data=RESET)

    keyboard = [[button_option_a], [button_option_b]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=WRONG_ACTION_TEXT, reply_markup=reply_markup)


async def send_default_response():
    print("Sending default fault response..")
    bot = Bot(TOKEN)
    await bot.send_message(chat_id=chat_id, text=WRONG_REPLY_TEXT)


async def send_failed_response():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, 'Failed to download your file, please send again.')


async def send_shefy_stom():
    bot = Bot(TOKEN)
    await bot.send_message(chat_id, 'Shefy Ne..'
                                    '\nאתה יכול רק ללחוץ על quit')


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


async def handle_vip_user_video(video_file_id):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters)
    await send_vip_user_goodbye()


async def handle_config_video(video_file_id):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters)
    await send_success_message()
    await send_config_menu()


async def handle_second_video(video_file_id):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters)
    update_chat_db({STATE: LAST_CHOICE})
    await send_nth_video_menu()


async def handle_first_video(video_file_id):
    parameters = [username, video_file_id]
    invoke_second_lambda(parameters)
    update_chat_db({STATE: SECOND_VIDEO})
    sentence = get_first_sentence_from_queue()
    print('THE TEXT IS: ' + str(sentence))
    await send_second_video_instructions(sentence)


def gender_suitble_text(RECEIVE_OK_TERMS):
    pass
