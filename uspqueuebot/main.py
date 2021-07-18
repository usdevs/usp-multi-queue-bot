import logging
from uspqueuebot.logic import howlong_command, join_command, leave_command, viewqueue_command
from uspqueuebot.constants import HELP_MESSAGE, INVALID_FORMAT_MESSAGE, NO_COMMAND_MESSAGE, START_MESSAGE
from uspqueuebot.credentials import ADMINS, ADMIN_CHAT_ID
from uspqueuebot.utilities import extract_user_details, get_message_type


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

    # obtain key message details
    message_type = get_message_type(body)
    chat_id, username = extract_user_details(body)

    # for debugging, set DEBUG_MODE to True
    if DEBUG_MODE:
        logger.warn("Debug mode has been activated.")
        text = str(body)
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        logger.warn("Event text has been sent to the admin.")
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

    if text == "/join":
        join_command(bot, chat_id, username)
        logger.info("Join command detected and processed.")
        return

    if text == "/leave":
        leave_command(bot, chat_id)
        logger.info("Leave command detected and processed.")
        return

    if text == "/howlong":
        howlong_command(bot, chat_id)
        logger.info("Howlong command detected and processed.")
        return

    if chat_id in ADMINS.values():
        if text == "/viewqueue":
            viewqueue_command(bot, chat_id)
            logger.info("Admin viewqueue command detected and processed.")
            return
        # intentionally no return here

    ## echo
    bot.send_message(chat_id=chat_id, text=text)
    return
