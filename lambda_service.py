import json
import boto3
from texts import STATE, USER_NAME


def invoke_second_lambda(parameters, state):
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
