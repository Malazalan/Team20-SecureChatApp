import pymongo
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError
import User
import importlib
importlib.reload(User)
from User import User

myclient = pymongo.MongoClient("mongodb://localhost:27017")

database = myclient["ChatAppDatabase"]
users = database.get_collection("users")

def write_user(username, email, password):
    password_hash = generate_password_hash(password)
   
    try:
        users.insert_one({'_id': username, 
                        'email': email,
                        'password': password_hash
                        })
    except DuplicateKeyError:
        print(f"Error: user with username '{username}' already exists")

def get_user(username):
    user = users.find_one({'_id': username})
    user_object = User(user)if user is not None else None
    return user_object

def get_user_ids(user):
    all_users = users.find()
    user_ids = []
    for current_user in all_users:
        current_id = current_user['_id']
        if current_id != user.get_id():
            user_ids.append(current_id)
    return user_ids

for current_username in ["Alice","Bob", "Charlie", "Dennis", "Eric", "Fatima"]:
    if get_user(current_username) is None:
        write_user(current_username, f"{current_username}@gmail.com", "password")

if get_user("John") is None:
    write_user("John", "john@gmail.com", "password")
