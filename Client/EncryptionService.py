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

# Dummy database to store user information (replace this with a real database)
USERS = {
    'sender_id': {
        'username': 'sender_username',
        'public_key': 'sender_public_key'
    },
    'receiver_id': {
        'username': 'receiver_username',
        'public_key': 'receiver_public_key'
    }
}


# Authenticate user based on token
def authenticate(token):
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        return USERS.get(payload.get('user_id'))
    except jwt.ExpiredSignatureError:
        abort(401, description="Token has expired.")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token.")


# AES-GCM + nonce + aes_key encryption function
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json(force=True)
    if 'plain_text' not in data or 'sender_id' not in data or 'receiver_id' not in data:
        abort(400, description="Missing required fields.")

    sender = authenticate(data['sender_id'])
    receiver = USERS.get(data['receiver_id'])
    if not sender or not receiver:
        abort(401, description="Invalid sender or receiver.")

    plain_text = data['plain_text']
    nonce = os.urandom(12)
    timestamp = datetime.datetime.utcnow().isoformat().encode('utf-8')  # ISO 8601 format

    try:
        aesgcm = AESGCM(aes_key)
        # Include timestamp in the additional authenticated data (AAD) to ensure integrity and authenticity
        encrypted_message = aesgcm.encrypt(nonce, plain_text.encode('utf-8'), timestamp)

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
            'timestamp': timestamp.decode('utf-8'),  # Return the ISO 8601 format string
            'sender': sender['username'],
            'receiver': receiver['username']
        }), 200
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        abort(500, description="Encryption failed.")


# AES-GCM + nonce + aes_key decryption function
@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json(force=True)
    if not all(k in data for k in ('encrypted_message', 'nonce', 'signature', 'timestamp', 'sender_id', 'receiver_id')):
        abort(400, description="Missing required fields for decryption.")

    sender = USERS.get(data['sender_id'])
    receiver = authenticate(data['receiver_id'])
    if not sender or not receiver:
        abort(401, description="Invalid sender or receiver.")

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

        return jsonify({
            'decrypted_message': decrypted_message.decode('utf-8'),
            'sender': sender['username'],
            'receiver': receiver['username']
        }), 200
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        abort(500, description="Decryption failed.")


# RSA public key encryption function
@app.route('/rsa_encrypt', methods=['POST'])
# RSA public key encryption function with signature
def rsa_encrypt_with_signature(public_key, private_key, plaintext):
    """
    Encrypts plaintext using RSA public key and signs the encrypted message.

    :param public_key: RSA public key for encryption.
    :param private_key: RSA private key for signing.
    :param plaintext: The plaintext message to encrypt.
    :return: Encrypted data as bytes, signature as bytes.
    """
    # Encrypt plaintext using RSA-OAEP
    encrypted_data = public_key.encrypt(
        plaintext.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Sign the encrypted data
    signature = private_key.sign(
        encrypted_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return encrypted_data, signature


# RSA private key decryption function with signature verification
def rsa_decrypt_with_signature(public_key, private_key, encrypted_data, signature):
    """
    Decrypts data using RSA private key and verifies the signature.

    :param public_key: RSA public key for signature verification.
    :param private_key: RSA private key for decryption.
    :param encrypted_data: The encrypted data to decrypt.
    :param signature: The signature to verify.
    :return: Decrypted plaintext as a string.
    """
    # Verify the signature
    public_key.verify(
        signature,
        encrypted_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    # Decrypt the data using RSA-OAEP
    decrypted = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode('utf-8')


if __name__ == '__main__':
    app.run(ssl_context='adhoc', port=5432)
