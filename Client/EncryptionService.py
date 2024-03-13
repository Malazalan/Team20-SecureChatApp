# Import necessary libraries
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from config import Config  # Configuration class from config.py
from cryptography.hazmat.backends import default_backend  # Explicitly import the default backend
import base64
from flask import Flask
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)                         
CORS(app)  # 这将允许所有域名跨域访问

# Load configurations from Config class in config.py
app.config.from_object(Config)

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# 加载私钥
with open("private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

# 加载公钥
with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )
    
# Load the secret key from configuration for additional operations (not used in this code snippet)
secret_key = app.config['SECRET_KEY']

# Function to generate a new RSA key pair
def generate_keys():
    try:
        # Generate private key with RSA algorithm
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,  # Defines the security level of the key
        )
        print("generate private_key is:", private_key)
        # Generate the public key from the private key
        public_key = private_key.public_key()

        # Serialize private key to PEM format
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key to PEM format
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Return serialized keys
        return pem_private, pem_public
    except Exception as e:
        print(f"Error generating keys: {e}")
        return None, None
    
# Generate keys
pem_private, pem_public = generate_keys()

# Ensure the keys were generated successfully
if pem_private is not None and pem_public is not None:
    # Save the serialized private key to a PEM file
    with open("private_key.pem", "wb") as f:
        f.write(pem_private)
    
    # Save the serialized public key to a PEM file
    with open("public_key.pem", "wb") as f:
        f.write(pem_public)
else:
    print("Failed to generate keys.")


# API endpoint for encrypting messages using RSA public key encryption and AES for the message itself
@app.route('/api/encrypt', methods=['POST'])
def encrypt_message():
    # Expecting 'message' and 'public_key_pem' in the request
    print("test")
    data = request.json
    print("data",data)
    message = data['message']
    print("message",message)
    #public_key_pem = data['public_key_pem'].encode()
    
    # Deserialize the public key from PEM format
    # public_key = serialization.load_pem_public_key(public_key_pem)
    # Generate a random AES key for symmetric encryption of the message
    aes_key = os.urandom(32)  # 256 bits key
    # Encrypt the AES key with the public RSA key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encrypt the actual message with AES in CFB mode
    iv = os.urandom(16)  # Initialization vector for AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()

    bencrypted_message = base64.b64encode(encrypted_message).decode('utf-8')
    bencrypted_aes_key = base64.b64encode(encrypted_aes_key).decode('utf-8')
    biv = base64.b64encode(iv).decode('utf-8')
    
    # Return the encrypted AES key, IV, and the encrypted message
    # Note: In practice, these should be encoded or serialized before sending
    return jsonify({
        "encrypted_aes_key": bencrypted_aes_key,
        "iv": biv,
        "encrypted_message": bencrypted_message
    })
    
    
# API endpoint for decrypting messages using RSA private key for the AES key and then decrypting the message with AES
@app.route('/api/decrypt', methods=['POST'])
def decrypt_message():
    # Expecting 'encrypted_aes_key', 'iv', and 'encrypted_message' in the request
    data = request.json
    encrypted_aes_key = data['encrypted_aes_key']
    iv = data['iv']
    encrypted_message = data['encrypted_message']
    
    # Deserialize the private key from PEM format stored in config
    private_key_pem = app.config['PRIVATE_KEY'].encode()
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)

    # Decrypt the AES key using the private RSA key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the actual message with AES using the decrypted AES key
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()

    # Return the decrypted message
    # Note: Ensure proper encoding and decoding of the message and keys
    return jsonify({"decrypted_message": decrypted_message.decode()})

# API endpoint for signing a message using the RSA private key
@app.route('/api/sign', methods=['POST'])
def sign_message():
    # Expecting 'message' in the request
    data = request.json
    message = data['message']
    
    # Deserialize the private key from PEM format stored in config
    private_key_pem = app.config['PRIVATE_KEY'].encode()
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)

    # Sign the message using the RSA private key with PSS padding and SHA-256 hashing
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Return the signature
    # Note: The signature should be properly encoded before sending if it's binary data
    return jsonify({"signature": signature})

# API endpoint for verifying a signature of a message using the RSA public key
@app.route('/api/verify', methods=['POST'])
def verify_signature():
    # Expecting 'message', 'signature', and optionally 'public_key_pem' in the request
    data = request.json
    message = data['message']
    signature = data['signature']
    public_key_pem = data.get('public_key_pem', app.config['PUBLIC_KEY']).encode()  # Use provided or default public key

    # Deserialize the public key from PEM format
    public_key = serialization.load_pem_public_key(public_key_pem)

    # Attempt to verify the signature of the message using the public key
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # If verification is successful
        return jsonify({"verified": True})
    except Exception as e:
        # If verification fails, return False with an error message
        return jsonify({"verified": False, "error": str(e)})

# Main entry point to run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5432)  # Run the app on port 5432 with debug mode enabled