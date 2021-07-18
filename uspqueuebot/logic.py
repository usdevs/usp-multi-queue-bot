import logging
from uspqueuebot.database import insert_user, remove_user
from uspqueuebot.constants import IN_QUEUE_MESSAGE, JOIN_SUCCESS_MESSAGE, LEAVE_SUCCESS_MESSAGE, NOT_IN_QUEUE_MESSAGE
from uspqueuebot.utilities import get_next_queue_number, get_queue, get_sha256_hash, is_in_queue

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

    queue_number = get_next_queue_number(queue)
    hashid = get_sha256_hash(chat_id)
    insert_user(hashid, chat_id, username, queue_number)
    bot.send_message(chat_id=chat_id, text=JOIN_SUCCESS_MESSAGE)
    logger.info("New user added to the queue.")
    return

def leave_command(bot, chat_id):
    queue = get_queue()
    if not is_in_queue(queue, chat_id):
        bot.send_message(chat_id=chat_id, text=NOT_IN_QUEUE_MESSAGE)
        logger.info("User not in queue tried to leave queue.")
        return
    
    hashid = get_sha256_hash(chat_id)
    remove_user(hashid)
    bot.send_message(chat_id=chat_id, text=LEAVE_SUCCESS_MESSAGE)
    logger.info("User removed from the queue.")
    return