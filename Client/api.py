from flask import Flask, request, jsonify, abort
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Loading Environment Variables
load_dotenv()

app = Flask(__name__)

# Read Fernet key from environment variable
key = os.getenv('FERNET_KEY')
if key is None:
    raise ValueError("No FERNET_KEY set for Flask application")
cipher_suite = Fernet(key)

# The rest of the Flask app...

