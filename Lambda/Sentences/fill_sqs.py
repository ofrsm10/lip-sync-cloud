import boto3

# Create an SQS client
sqs = boto3.client('sqs')

# Create a queue
response = sqs.create_queue(
    QueueName='sentence_queue'
)

# Retrieve the queue URL
queue_url = response['QueueUrl']
filename = "/Users/ofersimchovitch/PycharmProjects/lipSyncBeta/Lambda/Sentences/censored_4.txt"
with open(filename, 'r') as file:
    # Read each line in the file
    for line in file:
        if line.startswith(' '):
            continue
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=line
        )
print('Data inserted into SQS: sentence_queue')

