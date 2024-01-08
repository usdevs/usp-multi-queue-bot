import json
import logging
import os
import telegram
from dotenv import load_dotenv

load_dotenv()

from uspqueuebot.main import main

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}

ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}

def webhook(event):
    """
    Runs the Telegram webhook.
    https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html
    """
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TELEGRAM_TOKEN:
        logger.error('The TELEGRAM_TOKEN must be set')
        raise NotImplementedError
    
    bot = telegram.Bot(TELEGRAM_TOKEN)

    # Check if the webhook is set correctly
    webhook_info = bot.get_webhook_info()  
    desired_webhook_url = os.getenv("VERCEL_URL") + "/api/handler"

    # If the current webhook URL is not the desired one, update it
    if webhook_info.url != desired_webhook_url:
        bot.set_webhook(url=desired_webhook_url)
        logger.info(f"Webhook updated to: {desired_webhook_url}")
    else:
        logger.info("Webhook is already set correctly.")

    if event.get('httpMethod') == 'POST' and event.get('body'): 
        logger.info('Message received')
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)

        try:
            main(bot, update)
            
        except Exception as error:
            error_message = "There is an unhandled exception, please debug immediately.\n" + error.__str__()
            bot.send_message(chat_id=os.getenv("ADMIN_CHAT_ID"), text=error_message)
            logger.error(error_message)
            logger.error('Event: {}'.format(update.to_dict()))

        return OK_RESPONSE

    return ERROR_RESPONSE
