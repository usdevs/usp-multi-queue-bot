import hashlib
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from uspqueuebot.database import add_user_to_event, create_event, delete_all_events, delete_event, get_all_events, get_event_queue, get_last_command, record_last_command, remove_user_from_event, view_history

load_dotenv()

#=========================FUNCTIONS FOR DATA EXTRACTION=========================#
def get_message_type(body : dict):
    """
    Determines the Telegram message type

    Parameters
    ----------
    body: dic
        Body of webhook event
    
    Returns
    -------
    string
        Description of message type
    """

    if "message" in body.keys():
        if "text" in body["message"]:
            return "text"
        elif "sticker" in body["message"]:
            return "sticker"
    
    if "edited_message" in body.keys():
        return "edited_message"
    
    if "callback_query" in body.keys():
        return "callback_query"
    
    return "others"

def decimal_to_int(decimal):
    """
    Converts a json decimal to an integer.
    Mostly used to convert chat_id
    """
    
    integer = int(str(decimal))
    return integer
    
def extract_user_details(body : dict):
    """
    Obtains the chat ID from the event body

    Parameters
    ----------
    body: dic
        Body of webhook event
    
    Returns
    -------
    (int, str)
        Tuple containing chat ID and username of user
    """

    if "callback_query" in body.keys():
        chat_id = body["callback_query"]["message"]["chat"]["id"]
        username = body["callback_query"]["message"]["chat"]["username"]
    elif "edited_message" in body.keys():
        chat_id = body["edited_message"]["chat"]["id"]
        username = body["edited_message"]["chat"]["username"]
    else:
        chat_id = body["message"]["chat"]["id"]
        username = body["message"]["chat"]["username"]

    chat_id = decimal_to_int(chat_id)
    return (chat_id, username)

def get_sha256_hash(plaintext : str):
    """
    Hashes an object using SHA256. Usually used to generate hash of chat ID for lookup
    Parameters
    ----------
    plaintext: int or str
        Item to hash
    
    Returns
    -------
    str
        Hash of the item
    """

    hasher = hashlib.sha256()
    string_to_hash = str(plaintext)
    hasher.update(string_to_hash.encode('utf-8'))
    hash = hasher.hexdigest()
    return hash

#=========================FUNCTIONS FOR QUEUE MANIPULATION=========================#
def get_event_queue_from_database(event_id : str):
    '''
    Pre-process queue to be in the form of a list of tuples, sorted by queue number\n

    Parameters
    ----------
    event_id: str
        The event ID of the event to retrieve the queue from
        
    Returns
    -------
    queue: list
        Contains tuples in the form (chat_id, username) representing each 
        person in the queue
    '''
    raw_table = get_event_queue(event_id)
    queue = []
    for entry in raw_table:
        chat_id = decimal_to_int(entry["chat_id"])
        username = entry["username"]
        queue.append((chat_id, username))
    queue.sort()
    return queue

def get_next_queue_number(queue : list):
    '''
    Parameters
    ----------
    queue: list

    Returns
    -------
    the next (one-based) queue number or 1 if queue is empty
    '''
    return len(queue) + 1
    
def is_in_queue(queue : list, chat_id : int):
    '''
    Parameters
    ----------
    queue: list\n
    chat_id: int

    Returns
    -------
    True if the user is in the queue, False otherwise
    '''
    for entry in queue:
        if entry[0] == chat_id:
            return True
    return False

def get_first_chat_id(queue: list):
    '''
    Parameters
    ----------
    queue: list

    Returns
    -------
    the chat_id of the first person in the queue
    '''
    return queue[0][0]

def get_first_username(queue : list):
    '''
    Parameters
    ----------
    queue: list

    Returns
    -------
    the username of the first person in the queue
    '''
    return queue[0][1]

def get_position(queue : list, chat_id : int):
    '''
    Parameters
    ----------
    queue: list\n
    chat_id: int

    Returns
    ------- 
    the string position of the user in the queue,
    or "Not in queue" if user is not in queue
    '''
    ## position is equivalent to number of people ahead of user
    position = 0
    found = False
    for entry in queue:
        if entry[1] == chat_id:
            found = True
            break
        position += 1
    
    if not found:
        position = "Not in queue"
    return str(position)

def get_bump_queue(queue : list):
    '''
    Bumps the first person in the queue by a pre-defined number of positions in\n
    `constants.py`. Updates all the queue numbers accordingly.\n

    Parameters
    ----------
    queue: list

    Returns
    ------- 
    the modified queue
    '''
    bump_queue = queue[1:os.getenv("NUMBER_TO_BUMP") + 1]
    bump_queue.append(queue[0])
    bump_queue.append(queue[os.getenv("NUMBER_TO_BUMP") + 1:])
    return bump_queue

def create_event_in_database(event_name : str):
    '''
    Creates a new event and an empty associated queue in the database\n

    Parameters
    ----------
    event_name: str

    Returns
    -------
    event_id: str
        The event ID of the newly created event
    '''
    event_id = create_event(event_name)
    return event_id

def delete_event_from_database(event_id):
    '''
    Deletes an event from the database\n

    Parameters
    ----------
    event_id: str
        The event ID of the event to delete
    '''
    delete_event(event_id)
    return

def delete_all_events_from_database():
    '''
    Deletes all events from the database
    '''
    delete_all_events()
    return

def view_history_of_events_from_database(date):
    '''
    Returns a view of events before and inclusive of date using the event_date field
    '''
    return view_history(date)

def get_all_events_from_database():
    '''
    Returns all events in the database\n

    Returns
    -------
    events: list
        List of all events in the database

        Each event is of the form:
        {
            "_id": "17826cy78ey7",
            "event_name": "Concert",
            "event_date": "2024-01-01", # automatically initialised using datetime.now()
            "queue": [
                {"hashid": "user123", "chat_id": "chat123", "username": "user1"},
                {"hashid": "user456", "chat_id": "chat456", "username": "user2"},
                // ... More users
            ]
        }
        The returned list is of the form:
        [{}, {}, {}, {}] where each {} is a event.
    '''
    events = get_all_events()
    return events

def add_user_to_event_in_database(event_id : str, hashid : str, chat_id : int, username : str):
    '''
    Adds a user to the event queue in the database\n

    Parameters
    ----------
    event_id: str\n
    hashid: str\n
    chat_id: int\n
    username: str\n
    '''
    add_user_to_event(event_id, hashid, chat_id, username)


def remove_user_from_event_in_database(event_id : str, hashid : str):
    '''
    Removes a user from the event queue in the database\n

    Parameters
    ----------
    event_id: str\n
    hashid: str

    Returns
    ----------
    True if user was removed, False otherwise
    '''
    return remove_user_from_event(event_id, hashid)


def record_last_command_in_database(chat_id : int, command : str):
    '''
    Records the last command of a user given their chat_id and command\n

    Parameters
    ----------
    chat_id: int\n
    command: str
    '''
    record_last_command(chat_id, command)

def get_last_command_from_database(chat_id : int):
    '''
    Gets the last command of a user given their chat_id\n

    Parameters
    ----------
    chat_id: int\n

    Returns
    -------
    last_command: str
        The last command of the user
    '''
    last_command = get_last_command(chat_id)
    return last_command

def update_event_queue_in_database(new_queue : list, event_id):
    '''
    Updates the database with a new queue\n

    Parameters
    ----------
    new_queue: list
        The new queue to update the database with
    '''
    for (chat_id, username) in new_queue:
        hashid = get_sha256_hash(chat_id)
        add_user_to_event_in_database(event_id, hashid, chat_id, username)
    return

#=========================FUNCTIONS FOR EVENT SELECTION=========================#
def send_event_selection(update, last_instr : str):
    '''
    Generates a keyboard of events using an inline keyboard.

    Parameters: 
    ------------
    bot: The bot object from Telegram API.
    update: The update object from Telegram API.
    last_instr: The last instruction executed by the user from database.
    '''
    # Retrieve all events from the database
    events = get_all_events_from_database()  

    # Populates the keyboard with a bunch of buttons
    keyboard = [[InlineKeyboardButton(event['event_name'], callback_data=str(event['_id']))] for event in events]

    # This line wraps the keyboard in the InlineKeyboardMarkup, which is the format 
    # expected by Telegram API for inline keyboards. The reply_markup object will be passed to 
    # the bot's send_message function to display the inline keyboard to the user.
    reply_markup = InlineKeyboardMarkup(keyboard)

    # This sends a message to the user with the text "Please choose an event to join:". 
    # The reply_markup parameter is used to attach the inline keyboard to the message, allowing the 
    # user to make a selection from the available events.
    update.message.reply_text('Please choose an event to execute' + " " + last_instr + " " + 'on :', reply_markup=reply_markup)
