import hashlib

from uspqueuebot.constants import NUMBER_TO_BUMP
from uspqueuebot.database import get_table, remove_user


def get_message_type(body):
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
    
    return "others"

def decimal_to_int(decimal):
    """
    Converts a json decimal to an integer.
    Mostly used to convert chat_id
    """
    
    integer = int(str(decimal))
    return integer
    
def extract_user_details(body):
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

    if "edited_message" in body.keys():
        chat_id = body["edited_message"]["chat"]["id"]
        username = body["edited_message"]["chat"]["username"]
    else:
        chat_id = body["message"]["chat"]["id"]
        username = body["message"]["chat"]["username"]

    chat_id = decimal_to_int(chat_id)
    return (chat_id, username)

def get_sha256_hash(plaintext):
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

def get_queue():
    raw_table = get_table()
    queue = []
    for entry in raw_table["Items"]:
        queue_number = decimal_to_int(entry["queue_number"])
        chat_id = decimal_to_int(entry["chat_id"])
        username = entry["username"]
        queue.append((queue_number, chat_id, username))
    queue.sort()
    return queue

def get_next_queue_number(queue):
    queue_number = 0
    if len(queue) != 0:
        queue_number = queue[-1][0] + 1
    return queue_number
    
def is_in_queue(queue, chat_id):
    for entry in queue:
        if entry[1] == chat_id:
            return True
    return False

def get_position(chat_id, queue):
    position = 1
    found = False
    for entry in queue:
        if entry[1] == chat_id:
            found = True
            break
        position += 1
    
    if not found:
        position = "Not in queue"
    return str(position)

def get_next_queue(queue):
    to_delete = queue[0][1]
    hashid = get_sha256_hash(to_delete)
    remove_user(hashid)
    return queue[1:]

def get_first_chat_id(queue):
    if len(queue) == 0:
        return "None"
    return queue[0][1]

def get_first_username(queue):
    if len(queue) == 0:
        return "None"
    return queue[0][2]

def get_bump_queue(queue):
    ## for hongpei
    x = NUMBER_TO_BUMP
    return queue
