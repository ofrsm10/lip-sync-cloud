# Lip Sync Cloud - Video Processing Bot

A sophisticated Telegram bot system for collecting and processing lip-sync video data using AWS cloud infrastructure. The system enables users to contribute video samples that help train AI models for lip-reading and speech synthesis applications.

## 🏗️ Architecture Overview

The system follows a microservices architecture using AWS serverless components:

```
User ↔ Telegram API ↔ Alfred (Lambda) ↔ DynamoDB
                            ↕
                    Hermes (Lambda) ↔ S3 
                            ↕
                    SQS Queue (Sentences)
```

### Components

- **Alfred** - Main Telegram bot (AWS Lambda) that handles user interactions
- **Hermes** - Video processing service (AWS Lambda) for downloading and processing videos
- **DynamoDB** - Stores conversation state and user data
- **S3** - Stores uploaded video files
- **SQS** - Queue system for managing sentence prompts

## 🚀 Features

- **Multi-language Support** - Hebrew interface with English configuration
- **User Flow Management** - Guided conversation flow with state persistence
- **Video Processing** - Handles calibration and sentence videos
- **VIP User Support** - Special workflow for privileged users
- **Admin Controls** - Configuration and management interface
- **Accent Detection** - Collects accent information for better processing
- **Quality Control** - Input validation and error handling

## 🛠️ Technologies Used

- **Python 3.8+** - Core application language
- **AWS Lambda** - Serverless compute platform
- **AWS DynamoDB** - NoSQL database for state management
- **AWS S3** - Object storage for video files
- **AWS SQS** - Message queuing service
- **Telegram Bot API** - User interface platform
- **Boto3** - AWS SDK for Python

## 📋 Prerequisites

- AWS Account with appropriate permissions
- Telegram Bot Token
- Python 3.8 or higher
- AWS CLI configured

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/lip-sync-cloud.git
cd lip-sync-cloud
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AWS Configuration  
AWS_REGION=eu-north-1
WEBHOOK_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/stage/webhook
SQS_QUEUE_URL=https://sqs.region.amazonaws.com/your-account-id/sentence_queue
S3_BUCKET_NAME=your-s3-bucket-name
HERMES_LAMBDA_FUNCTION_NAME=your-hermes-lambda-function-name

# DynamoDB Tables
CHAT_TABLE_NAME=ChatDB
TEXT_TABLE_NAME=TextDB

# User Configuration
VIP_USER_ID=vip_user
ADMIN_USER_ID=admin_user
GUEST_USER_ID=guest_user
```

## 🏗️ AWS Deployment Guide

### Step 1: Create IAM Role

1. Go to AWS IAM Console
2. Create a new role for Lambda
3. Attach policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonSQSFullAccess`

### Step 2: Create DynamoDB Tables

#### ChatDB Table
```bash
aws dynamodb create-table \
    --table-name ChatDB \
    --attribute-definitions \
        AttributeName=user_name,AttributeType=S \
    --key-schema \
        AttributeName=user_name,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region your-region
```

#### TextDB Table
```bash
aws dynamodb create-table \
    --table-name TextDB \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region your-region
```

### Step 3: Create S3 Bucket

```bash
aws s3 mb s3://your-lipsync-bucket --region your-region
```

Create folder structure:
```bash
aws s3api put-object --bucket your-lipsync-bucket --key Sessions/
```

### Step 4: Create SQS Queue

```bash
aws sqs create-queue \
    --queue-name sentence_queue \
    --region your-region
```

### Step 5: Deploy Lambda Functions

#### Create Alfred Lambda (Main Bot)
1. Package the code:
```bash
zip -r alfred.zip . -x "*.git*" "__pycache__/*" "*.pyc"
```

2. Create Lambda function:
```bash
aws lambda create-function \
    --function-name AlfredTelegramBot \
    --runtime python3.8 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://alfred.zip \
    --region your-region
```

#### Create Hermes Lambda (Video Processing)
Create a separate Lambda function for video processing:

```bash
aws lambda create-function \
    --function-name HermesDayJob \
    --runtime python3.8 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
    --handler hermes_handler.lambda_handler \
    --zip-file fileb://hermes.zip \
    --region your-region
```

### Step 6: Create API Gateway

1. Create REST API:
```bash
aws apigateway create-rest-api \
    --name TelegramBotAPI \
    --region your-region
```

2. Create webhook resource and method
3. Deploy API to stage
4. Update `WEBHOOK_URL` in environment variables

### Step 7: Set Telegram Webhook

```bash
curl -X POST \
  "https://api.telegram.org/bot{BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_API_GATEWAY_URL"}'
```

## 🔐 Security Configuration

### Environment Variables Setup

The application uses environment variables for all sensitive data. Never commit actual tokens or credentials to version control.

Required environment variables:
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `AWS_REGION` - AWS region for your resources
- `WEBHOOK_URL` - API Gateway webhook URL
- `SQS_QUEUE_URL` - SQS queue URL
- `S3_BUCKET_NAME` - S3 bucket name
- `HERMES_LAMBDA_FUNCTION_NAME` - Video processing Lambda name

### AWS Permissions

Ensure your Lambda execution role has minimal required permissions:
- DynamoDB read/write access to your tables
- S3 read/write access to your bucket
- SQS send/receive/delete messages
- Lambda invoke permissions for Hermes function

## 🎯 Usage

### For Regular Users

1. Start conversation with the bot
2. Select gender and provide age
3. Indicate accent preferences
4. Record calibration video (tongue + smile)
5. Record sentence video with provided text
6. Optionally contribute additional sentences

### For VIP Users

1. Access advanced menu
2. Configure lighting and location
3. Choose between:
   - Calibration video
   - Sentence video with custom text

### For Administrators

1. Use `/config` command
2. Access management functions:
   - Clear chat database
   - Clear S3 bucket
   - Process test videos

## 🔧 Development

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`
3. Run tests:
```bash
python -m pytest tests/
```

### Code Structure

```
├── lambda_function.py      # Main Lambda handler
├── config.py              # Configuration and environment setup
├── db_service.py           # DynamoDB operations
├── s3_service.py           # S3 operations
├── sqs_service.py          # SQS operations
├── lambda_service.py       # Lambda invocation service
├── handle_message.py       # Text message handling
├── handle_video.py         # Video message handling
├── handle_callback.py      # Callback query handling
├── send_options.py         # Telegram message sending
└── texts.py               # Legacy text constants (deprecated)
```

### Adding New Features

1. Define new states in `config.py`
2. Add handlers in appropriate `handle_*.py` files
3. Update message routing in `lambda_function.py`
4. Add UI elements in `send_options.py`
5. Test thoroughly in development environment

## 📊 Monitoring

### CloudWatch Logs

Monitor Lambda function logs:
- Function errors and exceptions
- User interaction patterns
- Performance metrics

### DynamoDB Metrics

Monitor table performance:
- Read/write capacity utilization
- Throttling events
- Item counts

### S3 Storage

Track storage usage:
- Object counts
- Storage size
- Transfer rates

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Check Lambda function logs
- Verify webhook URL is correct
- Ensure Telegram token is valid

**Database errors:**
- Check DynamoDB table exists
- Verify IAM permissions
- Monitor capacity utilization

**Video processing failures:**
- Check S3 bucket permissions
- Verify Hermes Lambda function
- Monitor SQS queue for messages

### Debug Mode

Enable detailed logging by setting log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Handle errors gracefully

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review CloudWatch logs for errors

## 🔄 Updates and Maintenance

Regular maintenance tasks:
- Monitor AWS costs
- Update dependencies
- Review and rotate credentials
- Clean up old S3 objects
- Optimize DynamoDB capacity
