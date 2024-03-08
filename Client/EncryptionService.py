from flask import Flask, request, jsonify, abort
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import jwt
import logging
import datetime
from dotenv import load_dotenv

# Load environment variables for keys
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load AES key for encryption (simulating secure load from environment)
aes_key = os.urandom(32)

# Generate RSA keys for signing (simulating secure load)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

TIME_WINDOW = datetime.timedelta(minutes=5)  # Example time window for message validity

@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json(force=True)
    if 'message' not in data:
        abort(400, description="Missing required 'message' field.")

    message = data['message']
    nonce = os.urandom(12)
    timestamp = datetime.datetime.utcnow().isoformat().encode('utf-8')  # ISO 8601 format

    try:
        aesgcm = AESGCM(aes_key)
        # Include timestamp in the additional authenticated data (AAD) to ensure integrity and authenticity
        encrypted_message = aesgcm.encrypt(nonce, message.encode('utf-8'), timestamp)
        
        # Sign the encrypted message along with the timestamp
        signature = private_key.sign(
            encrypted_message + timestamp,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        
        return jsonify({
            'encrypted_message': encrypted_message.hex(),
            'nonce': nonce.hex(),
            'signature': signature.hex(),
            'timestamp': timestamp.decode('utf-8')  # Return the ISO 8601 format string
        }), 200
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        abort(500, description="Encryption failed.")

@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json(force=True)
    if not all(k in data for k in ('encrypted_message', 'nonce', 'signature', 'timestamp')):
        abort(400, description="Missing required fields for decryption.")

    try:
        encrypted_message = bytes.fromhex(data['encrypted_message'])
        nonce = bytes.fromhex(data['nonce'])
        signature = bytes.fromhex(data['signature'])
        timestamp = data['timestamp'].encode('utf-8')

        # Verify the timestamp is within the allowed time window
        message_datetime = datetime.datetime.fromisoformat(data['timestamp'])
        if datetime.datetime.utcnow() - message_datetime > TIME_WINDOW:
            abort(400, description="Message timestamp is outside of the allowed window.")
        
        # Verify the signature including the timestamp
        public_key.verify(
            signature,
            encrypted_message + timestamp,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        
        # Decrypt the message
        aesgcm = AESGCM(aes_key)
        decrypted_message = aesgcm.decrypt(nonce, encrypted_message, timestamp)
        
        return jsonify({'decrypted_message': decrypted_message.decode('utf-8')}), 200
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        abort(500, description="Decryption failed.")

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
