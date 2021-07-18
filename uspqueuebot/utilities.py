import hashlib

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

