import pymongo
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError

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

    
write_user("John", "john@gmail.com", "password")