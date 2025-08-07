import logging
import os

from telegram import Bot, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import boto3

# Telegram bot token
BOT_TOKEN = '5900828587:AAE9eVD3NCMQv9mhEx_mLUSX9PzVO9Ih2jE'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Replace with your webhook URL


def set_webhook(url):
    bot = Bot(token=BOT_TOKEN)
    response = bot.setWebhook(url=url)

    if response:
        print(response)
        print("Webhook set successfully.")
    else:
        print("Failed to set webhook.")


# Delete the webhook
def delete_webhook():
    bot = Bot(token=BOT_TOKEN)
    response = bot.deleteWebhook()

    if response:
        print("Webhook deleted successfully.")
    else:
        print("Failed to delete webhook.")


# Example usage

# Set the webhook

# Handler for '/start' command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot started. Ready to receive updates!")


# Handler for text messages
def process_message(update, context):
    text = update.message.text
    chat_id = update.effective_chat.id

    print(f"Received message from chat ID {chat_id}: {text}")

    # Reply with "OK"
    context.bot.send_message(chat_id=chat_id, text="OK")


def clear_s3_bucket():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('lipsync')
    bucket.objects.all().delete()


def clear_chat_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ChatTable')
    response = table.scan()
    items = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    for item in items:
        table.delete_item(Key={'user_name': item['user_name']})
        print(f"deleted item: {item['user_name']}")


def reset_word_counts():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WordsTable')

    response = table.scan()
    items = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    for item in items:
        word = item['word']
        table.update_item(
            Key={'word': word},
            UpdateExpression='SET #countAttr = :resetValue',
            ExpressionAttributeNames={'#countAttr': 'count'},
            ExpressionAttributeValues={':resetValue': 0}
        )


def upload_file(file_path):
    bot = Bot(token=BOT_TOKEN)
    try:
        # Upload the file to Telegram servers
        with open(file_path, 'rb') as file:
            file_id = bot.send_document(chat_id='YOUR_CHAT_ID', document=InputFile(file))
        logger.info(f"File uploaded successfully. File ID: {file_id}")
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")


def download_s3_folder(folder_name='Royshefy'):
    s3 = boto3.client('s3')
    bucket_name = 'lipsync'
    folder_name = 'Royshefy'
    destination_path = '/Users/ofersimchovitch/PycharmProjects/lipSyncBeta/Utils/user_sessions'
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    if 'Contents' in response:
        for file in response['Contents']:
            file_key = file['Key']
            file_name = os.path.join(destination_path, os.path.basename(file_key))

            s3.download_file(bucket_name, file_key, file_name)
            print(f"Downloaded file: {file_name}")
    else:
        print(f"No files found in the folder: {folder_name}")


def main():
    bot = Bot(token=BOT_TOKEN)
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(Filters.text, process_message)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    print("Bot started polling...")
    updater.idle()
    return


# Start the bot
if __name__ == '__main__':
    WEBHOOK_URL1 = 'https://vk3u73lrgi.execute-api.eu-north-1.amazonaws.com/dev/sqs-queue'
    WEBHOOK_URL2 = 'https://nkkv8ppzbe.execute-api.eu-north-1.amazonaws.com/default/LambdaTelegramBot'
    # delete_webhook()
    # main()
    # set_webhook(WEBHOOK_URL2)
    download_s3_folder()
    # clear_chat_table()
    # reset_word_counts()
    # clear_s3_bucket()
