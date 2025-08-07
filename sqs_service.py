import boto3

from texts import QUEUE_URL


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
