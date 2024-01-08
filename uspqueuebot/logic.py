import logging
import os
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

from uspqueuebot.utilities import (add_user_to_event_in_database, get_bump_queue, get_first_chat_id, get_first_username,
                                   get_next_queue_number, get_position,
                                   get_sha256_hash, is_in_queue, remove_user_from_event_in_database, update_event_queue_in_database)

load_dotenv()

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

# Note: Only use function from utilities.py. Do not use functions from database.py directly.
def create_new_event(bot : Bot, event_name : str, chat_id : int):
    '''
    Creates a new event in the database.
    Returns a response that displays the ongoing events to the user sorted by the event_date:

    For example, after the create command is given for event 3, the response should be:

    List of ongoing events:\n
    1. Event 1 (Created at: 11/12/2023)\n
    2. Event 2 (Created at: 12/12/2023)\n 
    3. Event 3 (Created at: 15/12/2023)

    where 11/12/2023 is the event_date
    '''
    #TODO @xinnnyeee
    pass
    
def delete_event_command(bot : Bot, event_id : int, chat_id : int):
    '''
    Deletes the selected event from the database. 
    Returns a response that displays the (remaining) ongoing events to the user sorted by the event_date:

    For example, after the delete command is given for event 3, the response should be:

    List of ongoing events:\n
    1. Event 1 (Created at: 11/12/2023)\n
    2. Event 2 (Created at: 12/12/2023)\n 

    where 11/12/2023 is the event_date
    '''
    #TODO @nhptrangg
    pass

def purge_database_command(bot: Bot, valid_date: datetime, chat_id: int):
    '''
    Deletes all events before and inclusive of `valid_date` from the database.
    Returns a response with format:
    
    All events before and inclusive of 11/12/2023 have been deleted
    '''
    #TODO @xinnnyeee
    pass

def view_history_command(bot: Bot, valid_date: datetime, chat_id: int):
    '''
    Returns a response that displays the (remaining) ongoing events before and inclusive of `valid_date` to the user sorted by the event_date:

    For example, after the view history command is given for 11/12/2023, the response should be:

    List of ongoing events:\n
    1. Event 1 (Created at: 11/12/2023)\n

    where 11/12/2023 is the event_date
    '''
    #TODO @nhptrangg
    pass

def join_command(bot, queue, chat_id, username, event_id):
    '''
    The bot adds the user to the selected event's queue.
    '''
    if is_in_queue(queue, chat_id):
        bot.send_message(chat_id=chat_id, text=os.getenv("IN_QUEUE_MESSAGE"))
        logger.info("User already in queue tried to join queue.")
        return

    queue_number = get_next_queue_number(queue)
    hashid = get_sha256_hash(chat_id)
    add_user_to_event_in_database(event_id, hashid, chat_id, username, queue_number)
    bot.send_message(chat_id=chat_id, text=os.getenv("JOIN_SUCCESS_MESSAGE"))
    logger.info("New user added to the queue.")
    return

def leave_command(bot, chat_id, event_id):
    '''
    The bot removes the user from the selected event's queue.
    '''
    hashid = get_sha256_hash(chat_id)
    if (remove_user_from_event_in_database(event_id, hashid)):
        bot.send_message(chat_id=chat_id, text=os.getenv("LEAVE_SUCCESS_MESSAGE"))
    else:
        bot.send_message(chat_id=chat_id, text=os.getenv("NOT_IN_QUEUE_MESSAGE"))
    return 

def howlong_command(bot, queue, chat_id):
    '''
    The bot informs the user of the length of the queue and how many people are before the querying user.
    '''
    position = get_position(queue, chat_id)
    queue_length = str(len(queue))
    if position == "Not in queue":
        position = queue_length
    message = os.getenv("POSITION_MESSAGE") + position + os.getenv("QUEUE_LENGTH_MESSAGE") + queue_length + "."
    bot.send_message(chat_id=chat_id, text=message)
    logger.info("Position and queue details sent to user.")
    return

def viewqueue_command(bot, queue, chat_id):
    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=os.getenv("EMPTY_QUEUE_MESSAGE"))
        logger.info("Empty queue has been sent to admin.")
        return
    message = "Queue:"
    for count, entry in enumerate(queue):
        username = entry[1]
        message += "\n"
        message += str(count + 1)
        message += ". "
        message += username
    bot.send_message(chat_id=chat_id, text=message)
    logger.info("Queue details has been sent to admin.")
    return

def next_command(bot, queue, chat_id, event_id):
    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=os.getenv("EMPTY_QUEUE_MESSAGE"))
        logger.info("Empty queue has been sent to admin.")
        return
    new_queue = queue[1:]
    next_username = get_first_username(new_queue)
    hash_id = get_sha256_hash(queue[0][0])
    remove_user_from_event_in_database(event_id, hash_id)
    bot.send_message(chat_id=chat_id, text=os.getenv("NEXT_SUCCESS_MESSAGE") + next_username)
    logger.info("Queue advanced by one user.")
    notify(bot, new_queue)
    return

def notify(bot, queue):
    count = -1
    for entry in queue[:os.getenv("NUMBER_TO_NOTIFY")]:
        count += 1
        chat_id = entry[0]
        if count == 0:
            bot.send_message(chat_id=chat_id, text=os.getenv("YOUR_TURN_MESSAGE"))
            continue
        bot.send_message(chat_id=chat_id, text=os.getenv("COME_NOW_MESSAGE") + str(count))
    logger.info("First few users has been informed of their queue status.")
    return

def bump_command(bot, queue, chat_id):
    if len(queue) == 0:
        bot.send_message(chat_id=chat_id, text=os.getenv("EMPTY_QUEUE_MESSAGE"))
        logger.info("Empty queue has been sent to admin.")
        return

    if len(queue) == 1:
        bot.send_message(chat_id=chat_id, text=os.getenv("USELESS_BUMP_MESSAGE"))
        logger.info("Admin has been informed that user is the only one in the queue.")
        return
    
    new_queue = get_bump_queue(queue)
    next_username = get_first_username(new_queue)
    update_event_queue_in_database(new_queue)
    inform_bumpee(bot, queue)
    bot.send_message(chat_id=chat_id, text=os.getenv("BUMP_SUCCESS_MESSAGE") + next_username)
    logger.info("First user in the queue has been bumped down.")
    notify(bot, new_queue)
    return

def inform_bumpee(bot, queue):
    chat_id = queue[0][1]
    bot.send_message(chat_id=chat_id, text=os.getenv("BUMPEE_MESSAGE"))
    logger.info("Bumpee has been informed of the bump.")
    return

def purge_command(bot, queue, chat_id, event_id):
    '''
    Removes every person in the queue but does not delete the event itself
    '''
    user_chat_id = get_first_chat_id(queue)
    while user_chat_id != "None":
        hashid = get_sha256_hash(user_chat_id)
        remove_user_from_event_in_database(event_id, hashid)
        bot.send_message(chat_id=user_chat_id, text=os.getenv("PURGE_MESSAGE"))
        queue = queue[1:]
        user_chat_id = get_first_chat_id(queue)
    bot.send_message(chat_id=chat_id, text=os.getenv("PURGE_SUCESSFUL_MESSAGE"))
    return

def broadcast_command(bot, queue, chat_id, message):
    if message == "":
        bot.send_message(chat_id=chat_id, text=os.getenv("BROADCAST_MESSAGE_MISSING_MESSAGE"))
        return
    user_chat_id = get_first_chat_id(queue)
    while user_chat_id != "None":
        bot.send_message(chat_id=user_chat_id, text=os.getenv("BROADCAST_MESSAGE") + message)
        queue = queue[1:]
        user_chat_id = get_first_chat_id(queue)
    bot.send_message(chat_id=chat_id, text=os.getenv("BROADCAST_SUCCESSFUL_MESSAGE"))
    return

