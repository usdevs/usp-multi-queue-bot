import logging

from uspqueuebot.constants import (BUMP_SUCCESS_MESSAGE, BUMPEE_MESSAGE,
                                   COME_NOW_MESSAGE, EMPTY_QUEUE_MESSAGE,
                                   IN_QUEUE_MESSAGE, JOIN_SUCCESS_MESSAGE,
                                   LEAVE_SUCCESS_MESSAGE, NEXT_SUCCESS_MESSAGE,
                                   NOT_IN_QUEUE_MESSAGE, NUMBER_TO_NOTIFY,
                                   POSITION_MESSAGE, QUEUE_LENGTH_MESSAGE,
                                   USELESS_BUMP_MESSAGE, YOUR_TURN_MESSAGE)
from uspqueuebot.database import insert_user, remove_user
from uspqueuebot.utilities import (get_bump_queue, get_first_chat_id,
                                   get_first_username, get_next_queue,
                                   get_next_queue_number, get_position,
                                   get_sha256_hash, is_in_queue)

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

def join_command(bot, queue, chat_id, username):
    if is_in_queue(queue, chat_id):
        bot.send_message(chat_id=chat_id, text=IN_QUEUE_MESSAGE)
        logger.info("User already in queue tried to join queue.")
        return

    queue_number = get_next_queue_number(queue)
    hashid = get_sha256_hash(chat_id)
    insert_user(hashid, chat_id, username, queue_number)
    bot.send_message(chat_id=chat_id, text=JOIN_SUCCESS_MESSAGE)
    logger.info("New user added to the queue.")

    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=YOUR_TURN_MESSAGE)
        logger.info("Newly added user is first in line.")
    
    return

def leave_command(bot, queue, chat_id):
    if not is_in_queue(queue, chat_id):
        bot.send_message(chat_id=chat_id, text=NOT_IN_QUEUE_MESSAGE)
        logger.info("User not in queue tried to leave queue.")
        return
    
    hashid = get_sha256_hash(chat_id)
    remove_user(hashid)
    bot.send_message(chat_id=chat_id, text=LEAVE_SUCCESS_MESSAGE)
    logger.info("User removed from the queue.")
    return

def howlong_command(bot, queue, chat_id):
    position = get_position(chat_id, queue)
    queue_length = str(len(queue))
    message = POSITION_MESSAGE + position + QUEUE_LENGTH_MESSAGE + queue_length + "."
    bot.send_message(chat_id=chat_id, text=message)
    logger.info("Position and queue details sent to user.")
    return

def viewqueue_command(bot, queue, chat_id):
    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=EMPTY_QUEUE_MESSAGE)
        logger.info("Empty queue has been sent to admin.")
        return
    message = "Queue:"
    count = 1
    for entry in queue:
        username = entry[2]
        message += "\n"
        message += str(count)
        message += ". "
        message += username
        count += 1
    bot.send_message(chat_id=chat_id, text=message)
    logger.info("Queue details has been sent to admin.")
    return

def next_command(bot, queue, chat_id):
    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=EMPTY_QUEUE_MESSAGE)
        logger.info("Empty queue has been sent to admin.")
        return
    new_queue = get_next_queue(queue)
    next_username = get_first_username(new_queue)
    bot.send_message(chat_id=chat_id, text=NEXT_SUCCESS_MESSAGE + next_username)
    logger.info("Queue advanced by one user.")
    notify(bot, new_queue)
    return

def notify(bot, queue):
    count = -1
    for entry in queue[:NUMBER_TO_NOTIFY]:
        count += 1
        if count == 0:
            bot.send_message(chat_id=chat_id, text=YOUR_TURN_MESSAGE)
            continue
        chat_id = entry[1]
        bot.send_message(chat_id=chat_id, text=COME_NOW_MESSAGE + str(count))
    logger.info("First few users has been informed of their queue status.")
    return

def bump_command(bot, queue, chat_id):
    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=EMPTY_QUEUE_MESSAGE)
        logger.info("Empty queue has been sent to admin.")
        return

    if len(queue) == 1:
        bot.send_message(chat_id=chat_id, text=USELESS_BUMP_MESSAGE)
        logger.info("Admin has been informed that user is the only one in the queue.")
        return
    
    new_queue = get_bump_queue(queue)
    next_username = get_first_username(new_queue)
    inform_bumpee(bot, queue)
    bot.send_message(chat_id=chat_id, text=BUMP_SUCCESS_MESSAGE + next_username)
    logger.info("First user in the queue has been bumped down.")
    notify(bot, new_queue)
    return

def inform_bumpee(bot, queue):
    chat_id = get_first_chat_id(queue)
    bot.send_message(chat_id=chat_id, text=BUMPEE_MESSAGE)
    logger.info("Bumpee has been informed of the bump.")
    return
