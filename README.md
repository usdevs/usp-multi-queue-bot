# USP Queue Bot

## Features

The USP Queue Bot simulates a physical queue that is managed using simple commands.
Users can join and leave the queue, while also keeping track of the queue length and their position in the queue.
Admins can also manage the queue by removing or bumping the first user in the queue.
The first few users in the queue would also be automatically informed as it is nearing their turn.
Responses from the bot are also in Singlish to keep the vibe fun and local.

## General Commands

### `/start`

Displays start message.

### `/help`

Displays help message with available commands.

### `/join`

Adds user into the queue.

### `/leave`

Removes user from the queue.

### `/howlong`

Displays the user's position in the queue and the overall queue length.

## Admin Commands

These commands would only work if the user is an admin.

### `/viewqueue`

Displays the entire ordered queue by usernames.

### `/next`

Removes the first person in the queue when they have been served.
The admin would be informed of the username of the user that is next in line.
The next few users would also be notified of their progress in the line.

### `/bump`

Bumps the first person in the queue by a few positions if they are late.
The admin would be informed of the username of the user that is next in line.
The next few users would also be notified of their progress in the line.

## Debugging

The following outlines the procedure for debugging.

1. In uspqueuebot/credentials.py, ensure `ADMIN_CHAT_ID` is accurate on line 4.
2. In uspqueuebot/main.py, change `DEBUG_MODE` to `True` on line 19.
3. In the command line, execute `severless deploy` or run `deploy.bat`.
4. From now on, all message metadata would be sent to the admin for debugging.
5. Users who sends messages to the bot will also receive an "under maintenance" response.
6. After debugging, change `DEBUG_MODE` in uspqueuebot/main.py back to `True`.
7. In the command line, execute `severless deploy` again.

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
3. Select "Permissions" and select the Lambda role under "Execution role".
4. In AWS IAM, select "Attach policies" under "Permissions" and "Permissions policies".
5. Search for and select "AmazonDynamoDBFullAccess" and "Attach policy".
6. Run the Telegram bot with `/start` and join the queue with `/join`.
7. From the AWS Console, select AWS DynamoDB.
8. Under "Tables", ensure that the "USPQueueBotTable" table has been created.
