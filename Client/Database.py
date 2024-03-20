import pymongo
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError
import User
import importlib
import pickle
importlib.reload(User)
from User import User
from cryptography.hazmat.primitives.asymmetric import rsa
from EncryptionService import get_public_key

flask_server_ip = "127.0.0.1"

myclient = pymongo.MongoClient("mongodb://localhost:27017")

database = myclient["ChatAppDatabase"]

users = database.get_collection("users")
invites = database.get_collection("invites")

#TODO: code a killswitch function that overwrites all the data in the database with 0's 

def write_user(username, password, browser_fingerprint, current_room=None):
    password_hash = generate_password_hash(password)
   
    try:
        users.insert_one({'_id': username,
                        'password': password_hash,
                        'browser_fingerprint': browser_fingerprint,
                        'current_room': current_room,
                        "ip_address": flask_server_ip,
                        "public_key_e": str(get_public_key().public_numbers().e),
                        "public_key_n": str(get_public_key().public_numbers().n)
                        })
    except DuplicateKeyError:
        print(f"Error: user with username '{username}' already exists")

def write_invite(username, invite_id):
    try:
        invites.insert_one({'_id': username, 
                        'invite_id': invite_id,
                        })
    except DuplicateKeyError:
        print(f"Error: user with username '{username}' already exists")

'''def get_room(username):
    user = users.find_one({'_id': username})
    #user_object = User(user)if user is not None else None
    room = user['current_room']
    return room'''

def set_room(username, room):
    # Update the current_room field for the user
    users.update_one({'_id': username}, {'$set': {'current_room': room}})

def get_user(username):
    user = users.find_one({'_id': username})
    user_object = User(user)if user is not None else None
    return user_object

def get_invite(username):
    invite = invites.find_one({'_id': username})
    return invite

def invite_exists(username):
    invite = invites.find_one({'_id': username})
    return invite if invite else None

def remove_invite(username):
    result = invites.delete_one({'_id': username}) #TODO: make this overwrite the entry with 0's first before deleting it?
    return (True if result.deleted_count == 1 else False)  


def get_user_ids(user):
    all_users = users.find()
    user_ids = []
    for current_user in all_users:
        current_id = current_user['_id']
        if current_id != user.get_id():
            user_ids.append(current_id)
    return user_ids


def add_public_key_to_user(user_id, public_key):
    """
    Add the provided RSA public key to the specified user in the MongoDB database.

    Args:
    - user_id: ID of the user to add the public key to
    - public_key: RSA public key object

    Returns:
    - True if successful, False otherwise
    """
    try:
        # Serialize the public key object
        serialized_public_key = pickle.dumps(public_key)

        # Update the user document to add the public key field
        users.update_one({"_id": user_id}, {"$set": {"public_key": serialized_public_key}})
        return True
    except Exception as e:
        print("Error adding public key to user:", e)
        return False


def add_public_key_to_all_users(public_key):
    """
    Add the provided RSA public key to all users in the MongoDB database.

    Args:
    - public_key: RSA public key object

    Returns:
    - True if successful, False otherwise
    """
    try:
        # Extract public key components
        e = public_key.public_numbers().e
        n = public_key.public_numbers().n

        # Convert integers to string representation
        e_str = str(e)
        n_str = str(n)

        # Update all user documents to add the public key fields
        users.update_many({}, {"$set": {"public_key_e": e_str, "public_key_n": n_str}})
        return True
    except Exception as e:
        print("Error adding public key to all users:", e)
        return False

def get_public_key_from_user(user_id):
    """
    Retrieve the RSA public key from the specified user document in the MongoDB database.

    Args:
    - user_id: ID of the user to retrieve the public key from

    Returns:
    - RSA public key object if found, None otherwise
    """
    try:
        # Find the user document in the database
        user_doc = users.find_one({"_id": user_id})
        if user_doc and "public_key_e" in user_doc and "public_key_n" in user_doc:
            # Deserialize the public key object
            e = int(user_doc['public_key_e'])
            n = int(user_doc['public_key_n'])

            # Reconstruct the RSA public key
            public_numbers = rsa.RSAPublicNumbers(e, n)
            public_key = public_numbers.public_key()
            print(public_key)
            return public_key
        else:
            print("Public key not found for the user.")
            return None
    except Exception as e:
        print("Error retrieving public key from user:", e)
        return None

'''for current_username in ["Alice","Bob", "Charlie", "Dennis", "Eric", "Fatima"]:
    if get_user(current_username) is None:
        write_user(current_username, f"{current_username}@gmail.com", "password")'''
