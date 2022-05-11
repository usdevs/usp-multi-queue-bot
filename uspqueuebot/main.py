import logging

from uspqueuebot.constants import (HELP_MESSAGE, INVALID_COMMAND_MESSAGE,
                                   INVALID_FORMAT_MESSAGE, NO_COMMAND_MESSAGE,
                                   START_MESSAGE, UNDER_MAINTENANCE_MESSAGE)
from uspqueuebot.credentials import ADMIN_CHAT_ID, ADMINS
from uspqueuebot.logic import (broadcast_command, bump_command, howlong_command, join_command,
                               leave_command, next_command, purge_queue, viewqueue_command)
from uspqueuebot.utilities import (extract_user_details, get_message_type,
                                   get_queue)

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

DEBUG_MODE = False

def main(bot, body):
    """
    Runs the main logic of the Telegram bot
    """
    
    # for privacy issues, this is commented out
    #logger.info('Event: {}'.format(body))

    # manage updates (https://core.telegram.org/bots/api#getting-updates)
    if "update_id" in body.keys() and len(body.keys()) == 1:
        logger.info("An update_id message has been sent by Telegram.")
        logger.error('Event: {}'.format(body))
        return
    
    # obtain key message details
    message_type = get_message_type(body)
    chat_id, username = extract_user_details(body)

    # for debugging, set DEBUG_MODE to True
    if DEBUG_MODE:
        logger.warn("Debug mode has been activated.")
        text = str(body)
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        logger.warn("Event text has been sent to the admin.")
        bot.send_message(chat_id=chat_id, text=UNDER_MAINTENANCE_MESSAGE)
        logger.warn("Maintenance message has been sent to user.")
        return

    # check for file types we cannot handle
    if not message_type == "text":
        bot.send_message(chat_id=chat_id, text=INVALID_FORMAT_MESSAGE)
        logger.info("A message of invalid format has been sent.")
        return
    
    # reject all non-commands
    text = body["message"]["text"]
    if text[0] != "/":
        bot.send_message(chat_id=chat_id, text=NO_COMMAND_MESSAGE)
        logger.info("No command detected.")
        return

    # start command
    if text == "/start":
        bot.send_message(chat_id=chat_id, text=START_MESSAGE)
        logger.info("Start command detected and processed.")
        return

    # help command
    if text == "/help":
        bot.send_message(chat_id=chat_id, text=HELP_MESSAGE)
        logger.info("Help command detected and processed.")
        return

    queue = get_queue()

    # join command
    if text == "/join":
        join_command(bot, queue, chat_id, username)
        logger.info("Join command detected and processed.")
        return

    # leave command
    if text == "/leave":
        leave_command(bot, queue, chat_id)
        logger.info("Leave command detected and processed.")
        return

    # howlong command
    if text == "/howlong":
        howlong_command(bot, queue, chat_id)
        logger.info("Howlong command detected and processed.")
        return

    # admin commands
    if chat_id in ADMINS.values():
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
            purge_queue(bot, queue, chat_id)
            logger.info("Purge command detected and processed.")
            return

        if text[:10] == "/broadcast":
            broadcast_command(bot, queue, chat_id, text[10:])
            logger.info("Broadcast command detected and processed.")
            return

        # intentionally no return here

    ## invalid command
    bot.send_message(chat_id=chat_id, text=INVALID_COMMAND_MESSAGE)
    return
