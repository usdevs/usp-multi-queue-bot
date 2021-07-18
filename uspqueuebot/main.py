import logging
from uspqueuebot.constants import INVALID_FORMAT_MESSAGE, NO_COMMAND_MESSAGE
from uspqueuebot.credentials import ADMIN_CHAT_ID
from uspqueuebot.utilities import extract_chat_id, get_message_type


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
    chat_id = extract_chat_id(body)

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


    ## echo
    bot.send_message(chat_id=chat_id, text=text)
    return