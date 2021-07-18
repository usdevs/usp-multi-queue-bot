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

def extract_chat_id(body):
    """
    Obtains the chat ID from the event body

    Parameters
    ----------
    body: dic
        Body of webhook event
    
    Returns
    -------
    int
        Chat ID of user
    """

    if "edited_message" in body.keys():
        chat_id = body["edited_message"]["chat"]["id"]
    else:
        chat_id = body["message"]["chat"]["id"]
    return chat_id
