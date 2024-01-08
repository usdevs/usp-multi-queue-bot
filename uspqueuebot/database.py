import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

'''
The stucture of the Event object is as follows:
Queue number is implicit from array index + 1
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
'''
'''
The structure of the User object is as follows:
Queue number is implicit from array index + 1
{
    "_id": "284873nuyu43",
    "chat_id": "chat123",
    "last_command": "/join",
}
'''
# Configure logging
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

# Setup MongoDB client
client = MongoClient(os.getenv("MONGO_URL"))
db = client.USPQUEUEBOT  # Change to your database name
events_collection = db.Events  # Using the Events collection
users_collection = db.Users  # Using the Users collection

# Function to create a new event
def create_event(event_name):
    event_document = {
        "event_name": event_name,
        "event_date": datetime.now(),
        "queue": []
    }
    result = events_collection.insert_one(event_document)
    logger.info(f"New event created with ID: {result.inserted_id}")
    return result.inserted_id   

def delete_event(event_id):
    events_collection.delete_one({"_id": ObjectId(event_id)})
    logger.info("Event deleted.")
    return 

def delete_all_events():
    '''
    Deletes all events in the database
    '''
    #TODO @xinnnyeee for `purge_database_command`
    pass

def view_history(date):
    '''
    Filter the events collection by date and return the events that are before and inclusive of the date
    '''
    #TODO @nhptrangg for `view_history_command`
    pass

# Function to get all events, result can be displayed using an inline keyboard, with the callback data 
# being the _id fields
def get_all_events():
    try:
        events = list(events_collection.find({}))
        logger.info("All events have been retrieved and returned.")
        return events  # Returns a list of event documents
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []

# Function to add a user to an event queue
def add_user_to_event(event_id, hashid, chat_id, username):
    user_details = {"hashid": hashid, "chat_id": chat_id, "username": username}
    events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$push": {"queue": user_details}}
    )
    logger.info("New user added to event queue.")
    return 

def remove_user_from_event(event_id, hashid):
    '''
    Returns true if the user was removed from the event queue else false
    '''
    result = events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$pull": {"queue": {"hashid": hashid}}}
    )
    if result.modified_count == 1:
        logger.info("User removed from event queue.")
        return True
    elif result.modified_count == 0:
        logger.info("No user removed from event queue. User does not exist in queue.")
        return False
    else:
        logger.exception("Multiple instances of the same user existed and have now been removed from event queue. Please check database.")
        return True 

# Function to get the queue of a specific event
def get_event_queue(event_id):
    '''
    Returns the queue of a specific event in array format
    [
        {"hashid": "user123", "chat_id": "chat123"},
        {"hashid": "user456", "chat_id": "chat456"}
        // ... More users
    ]
    '''
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if event:
        return event.get("queue", [])
    else:
        logger.error("Event not found.")
        return []

def record_last_command(chat_id, command):
    '''
    Records the last command of a user given their chat_id and command
    '''
    users_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"last_command": command}},
        upsert=True
    )
    logger.info("Last command, {} of user {} recorded.".format(command, chat_id))
    return 

def get_last_command(chat_id):
    '''
    Gets the last command of a user given their chat_id \n
    Returns:
        Empty string if user not found or no last command \n
        String of last command if user found and there is a last command
    '''
    user = users_collection.find_one({"chat_id": chat_id})
    if user:
        return user.get("last_command", "")
    else:
        logger.error("User not found.")
        return ""
    
# # Example usage
# if __name__ == "__main__":
#     # Example of creating a new event
#     event_id = create_event("Concert")

#     # Example of adding a user to the event queue
#     add_user_to_event(event_id, "user123", "chat123", "user1", 1)

#     # Example of removing a user from the event queue
#     remove_user_from_event(event_id, "user123")

#     # Example of retrieving the event queue
#     queue = get_event_queue(event_id)
#     print("Event Queue:", queue)

#     # Example of recording the last command of a user
#     record_last_command("chat123", "/join")

#     # Example of retrieving the last command of a user
#     last_command = get_last_command("chat123")
#     print("Last Command:", last_command)

#     # Example of deleting an event
#     delete_event(event_id)
#     print("Event Deleted")
