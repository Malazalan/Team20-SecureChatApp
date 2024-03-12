# Team20-SecureChatApp



## Secure Messaging API

EncryptionService.py this Flask application provides a RESTful API for secure messaging, utilizing RSA for key management and AES for message encryption, ensuring confidentiality, integrity, and authentication of messages.

### Features

- **RSA Key Pair Generation**: Generate RSA public and private key pairs.
- **Message Encryption**: Encrypt messages using AES encryption with keys secured by RSA.
- **Message Decryption**: Decrypt messages encrypted by this service.
- **Message Signing**: Sign messages using a private RSA key to ensure message integrity and non-repudiation.
- **Signature Verification**: Verify the signature of a message using the corresponding public RSA key.

### Installation

To run this application, you'll need Python 3 and pip installed on your system.

1. Clone the repository:
git clone https://github.com/Malazalan/Team20-SecureChatApp/
cd Client/

2. Install the required Python packages:
pip install -r requirements.txt

3. Start the Flask application:
python EncryptionService.py

### Test

1. Curl
```shell
cd /Team20-SecureChatApp/Client/
curl -X POST http://localhost:5432/api/encrypt \\n-H "Content-Type: application/json" \\n-d '{"message": "Hello, World!"}'\n
```

