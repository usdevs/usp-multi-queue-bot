import logging
import os
import json
from dotenv import load_dotenv
import datetime
from uspqueuebot.logic import (broadcast_command, bump_command, create_new_event, delete_event_command, howlong_command, join_command,
                               leave_command, next_command, purge_command, purge_database_command, view_history_command, viewqueue_command)
from uspqueuebot.utilities import (extract_user_details, get_event_queue_from_database, get_last_command_from_database, get_message_type, record_last_command_in_database, send_event_selection)

load_dotenv()

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

DEBUG_MODE = False

def main(bot, update):
    """
    Runs the main logic of the Telegram bot
    """
    body = update.to_dict()

    if "update_id" in body.keys() and len(body.keys()) == 1:
        handle_invalid_updates(body)
    
    # obtain key message details
    message_type = get_message_type(body)
    chat_id, username = extract_user_details(body)

    # for debugging, set DEBUG_MODE to True
    if DEBUG_MODE:
        handle_debug_mode(bot, body, chat_id)
        return 
    
    if message_type == "text":
        handle_text_message(bot, body, update, chat_id)
        return
    
    # When a user presses a button in an inline keyboard of a Telegram bot, the bot receives an update that is categorized as a "callback query." The callback query contains various pieces of information, including the callback_data associated with the button pressed.
    if message_type == "callback_query":
        handle_callback_query(bot, chat_id, username, update)
        return

    # file types we cannot handle
    handle_invalid_message_type(bot, chat_id)   
    return 

def handle_invalid_updates(body):
    logger.info("An update_id message has been sent by Telegram.")
    logger.error('Event: {}'.format(body))
    return

def handle_debug_mode(bot, body, chat_id):
    logger.warn("Debug mode has been activated.")
    text = str(body)
    bot.send_message(chat_id=os.getenv("ADMIN_CHAT_ID"), text=text)
    logger.warn("Event text has been sent to the admin.")
    bot.send_message(chat_id=chat_id, text=os.getenv("UNDER_MAINTENANCE_MESSAGE"))
    logger.warn("Maintenance message has been sent to user.")
    return

def handle_invalid_message_type(bot, chat_id):
    bot.send_message(chat_id=chat_id, text=os.getenv("INVALID_FORMAT_MESSAGE"))
    logger.info("A message of invalid format has been sent.")
    return

def handle_callback_query(bot, chat_id, username, update):
    query = update.callback_query
    query.answer()  # It's good practice to answer the callback query

    # Extract and process the callback data
    event_id = query.data  
    queue = get_event_queue_from_database(event_id)
    text = get_last_command_from_database(chat_id)

    # join command
    if text == "/join":
        join_command(bot, queue, chat_id, username, event_id)
        logger.info("Join command detected and processed.")
        return

    # leave command
    if text == "/leave":
        leave_command(bot, chat_id, event_id)
        logger.info("Leave command detected and processed.")
        return

    # howlong command
    if text == "/howlong":
        howlong_command(bot, queue, chat_id)
        logger.info("Howlong command detected and processed.")
        return

    admins_str = os.getenv('ADMINS')
    admins_dict = json.loads(admins_str.replace("'", "\"")) # replacing single quotes to double quotes for valid JSON
    # admin commands
    if chat_id in admins_dict.values():
        # viewqueue command
        if text == "/viewqueue":
            viewqueue_command(bot, queue, chat_id)
            logger.info("Admin viewqueue command detected and processed.")
            return
        
        # next command
        if text == "/next":
            next_command(bot, queue, chat_id)
            logger.info("Next command detected and processed.")
            return

        # bump command
        if text == "/bump":
            bump_command(bot, queue, chat_id)
            logger.info("Bump command detected and processed.")
            return

        if text == "/purge":
            purge_command(bot, queue, chat_id)
            logger.info("Purge command detected and processed.")
            return

        if text[:10] == "/broadcast":
            broadcast_command(bot, queue, chat_id, text[10:])
            logger.info("Broadcast command detected and processed.")
            return
        
        if text == "/delete":
            delete_event_command(bot, event_id, chat_id)
            logger.info("Delete command detected and processed.")
            return
        
    ## invalid command
    bot.send_message(chat_id=chat_id, text=INVALID_COMMAND_MESSAGE)
    return
