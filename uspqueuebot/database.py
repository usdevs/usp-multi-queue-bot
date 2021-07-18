import logging
import boto3

from boto3.dynamodb.conditions import Attr

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

# Setting up client with AWS
client = boto3.resource("dynamodb")
TABLE_NAME = "USPQueueBotTable"
table = client.Table(TABLE_NAME)

def create_table():
    """
    Creates a DynamoDB table
    """

    try:
        client.create_table(
            TableName = TABLE_NAME,
            KeySchema = [
                {
                    "AttributeName": 'hashid',
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions = [
                {
                    "AttributeName": "hashid",
                    "AttributeType": "S"
                }
            ],
            ProvisionedThroughput = {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        logger.info("Table named " + TABLE_NAME + " was created in DynamoDB.")
    except:
        logger.info("Table named " + TABLE_NAME + " already exists in DynamoDB.")
    return

def get_table():
    """
    Retrieve all contents of the table

    Returns
    -------
    dic
        Response from scan requeston DynamoDB
    """
    try:
        response = table.scan()
        logger.info("All entries have been retrieved and returned.")
        return response
    except:
        create_table()
        response = get_table()
        return response    

def insert_user(hashid, chat_id, username, queue_number):
    """
    Insert a new entry into the table
    """
    table.update_item(
        Key = {"hashid": hashid},
        UpdateExpression = "SET {} = :val1, {} =:val2, {} = :val3".format("chat_id", "username", "queue_number"),
        ExpressionAttributeValues = {":val1": chat_id, ":val2": username, ":val3": queue_number}
        )
    logger.info("New entry successfully added into DynamoDB.")

def remove_user(hashid):
    """
    Removes an entry from the table using hashid
    """

    table.delete_item(
        Key = {"hashid": hashid}
    )
    logger.info("User has been successfully removed from the database.")
