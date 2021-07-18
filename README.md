# USP Queuing Bot

## Features

## General Commands

## Admin Commands

These commands would only work if the user is an admin.

## Debugging

The following outlines the procedure for debugging.

1. In asafespace/main.py, ensure `ADMIN_CHAT_ID` is accurate on line 17.
2. In the same file, change `DEBUG_MODE` to `True` on line 18.
3. In the command line, execute `severless deploy`.
4. From now on, all message metadata would be sent to the admin for debugging.
5. Students who sends messages to the bot will also receive an "under maintenance" response.
6. After debugging, change `DEBUG_MODE` in asafespace/main.py back to `True`.
7. In the command line, execute `severless deploy` again.
8. Admins can use the `/admin` command in the bot to broadcast a message to all students.

## AWS and Serverless Deployment

### Installing

```lang-none
# Clone the repository into your local drive
# Open the command window in the bot file location

# Install the Serverless Framework
$ npm install serverless -g

# Install the necessary plugins
$ npm install
```

### Deploying

```lang-none
# Update AWS CLI in .aws/credentials

# Deploy it!
$ serverless deploy

# With the URL returned in the output, configure the Webhook
$ curl -X POST https://<your_url>.amazonaws.com/dev/set_webhook
```

### AWS Configurations

1. From the AWS Console, select AWS Lambda.
2. In AWS Lambda, select "usp-queue-bot-dev-webhook".
3. Select "Permissions" and select the Lambda role under "Execution role"
4. In AWS IAM, select "Attach policies" under "Permissions" and "Permissions policies"
5. Search for and select "AmazonDynamoDBFullAccess" and "Attach policy"
6. Run the Telegram bot with `/start` and register with `/register`
7. The first attempt at registration should return an error.
8. From the AWS Console, select AWS DynamoDB.
9. Under "Tables", ensure that the "USPQueueBotTable" table has been created.
10. Re-register with `/register`, and registration should be successful.
