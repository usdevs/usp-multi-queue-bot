import logging
from uspqueuebot.database import insert_user
from uspqueuebot.constants import IN_QUEUE_MESSAGE, JOIN_SUCCESS_MESSAGE
from uspqueuebot.utilities import get_queue, get_sha256_hash, is_in_queue

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

def join_command(bot, chat_id, username):
    queue = get_queue()
    if is_in_queue(queue, chat_id):
        bot.send_message(chat_id=chat_id, text=IN_QUEUE_MESSAGE)
        logger.info("User already in queue tried to join queue.")
        return

    queue_number = 0
    if len(queue) != 0:
        queue_number = queue[-1][0] + 1
    hashid = get_sha256_hash(chat_id)
    insert_user(hashid, chat_id, username, queue_number)
    bot.send_message(chat_id=chat_id, text=JOIN_SUCCESS_MESSAGE)
    logger.info("New user added to the queue.")
    return