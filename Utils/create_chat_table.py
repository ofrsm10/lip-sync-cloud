import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.create_table(
    TableName='ChatTable',
    KeySchema=[
        {
            'AttributeName': 'messageId',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'messageId',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'ttl',
            'AttributeType': 'N'  # Numeric attribute for TTL values
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    },
    TimeToLiveSpecification={
        'Enabled': True,
        'AttributeName': 'ttl'  # Specify the TTL attribute
    }
)


def insert_chat_item(chat_item):
    current_time = int(time.time())
    expiration_time = current_time + (20 * 60)  # Add 20 minutes to the current time
    chat_item['ttl'] = expiration_time
    table.put_item(Item=chat_item)
