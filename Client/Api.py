from flask import Flask, request, jsonify, abort
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

from flask_mail import Mail

from config import config

# Loading Environment Variables
load_dotenv()

app = Flask(__name__)

app.config.from_object(config)
mail = Mail(app)

# Read Fernet key from environment variable
key = os.getenv('FERNET_KEY')
if key is None:
    raise ValueError("No FERNET_KEY set for Flask application")
cipher_suite = Fernet(key)

# The rest of the Flask app...

