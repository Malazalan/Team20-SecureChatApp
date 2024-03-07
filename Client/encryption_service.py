from flask import Flask, request, jsonify, abort
from cryptography.fernet import Fernet
import os

# IMPORTANT SECURITY NOTE: Ensure that FERNET_KEY is obtained from a secure source and that it should not be hard-coded in code or committed to a version control system.
# So here I save it in an environment variable or use a configuration file and make sure the configuration file is not uploaded to a public code repository.

app = Flask(__name__)

# Security Configuration - Setting up a secure key for your Flask application
app.config['SECRET_KEY'] = os.urandom(24)

# Key persistence - read from environment variable or file
key = os.environ.get('FERNET_KEY')
if key is None:
    raise ValueError("No FERNET_KEY set for Flask application")
cipher_suite = Fernet(key)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        data = request.get_json()
        if 'message' not in data or not data['message']:
            return jsonify({'error': 'No message provided'}), 400

        encrypted_text = cipher_suite.encrypt(data['message'].encode('utf-8'))
        return jsonify({'encrypted_message': encrypted_text.decode('utf-8')}), 200
    except Exception as e:
        # More detailed error handling
        abort(500, description=str(e))

@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        data = request.get_json()
        if 'encrypted_message' not in data or not data['encrypted_message']:
            return jsonify({'error': 'No encrypted_message provided'}), 400

        decrypted_text = cipher_suite.decrypt(data['encrypted_message'].encode('utf-8'))
        return jsonify({'message': decrypted_text.decode('utf-8')}), 200
    except Exception as e:
        # More detailed error handling
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run()

