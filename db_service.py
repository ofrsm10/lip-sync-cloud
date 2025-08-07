import boto3

from texts import CHAT_TABLE, USER_NAME, ADMIN

db_source = boto3.resource('dynamodb')


def get_from_chat_db(data, username):
    chat_table = db_source.Table(CHAT_TABLE)
    retrieved_item = run_get_loop(chat_table, {USER_NAME: username})
    if retrieved_item:
        return retrieved_item.get(data)
    else:
        return None


def update_chat_db(data_values, username):
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


def delete_conversation(username):
    chat_table = db_source.Table(CHAT_TABLE)
    print(f"Deleting user_name: {username} from ChatDB")
    response = chat_table.delete_item(Key={USER_NAME: username})
    # i = 0
    # while not response.get('ResponseMetadata').get('HTTPStatusCode') == 200 and i < 5:
    #     i += 1
    #     response = chat_table.delete_item(Key={USER_NAME: username})


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
