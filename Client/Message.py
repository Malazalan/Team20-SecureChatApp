import re
import time

from EncryptionService import rsa_encrypt, rsa_decrypt, get_private_key, get_public_key

plaintext_size = 180
ciphertext_size = 256
split_char = b'\x00'


def cleanse_message_(message):
    sql_pattern = re.compile(r'(\'|").*?(select|or).*?(\'|")', re.IGNORECASE | re.DOTALL)

    xss_found = False

    sql_found = bool(sql_pattern.search(message))

    # Cleanse message
    while "<script>" in message or "</script>" in message:
        message = message.replace("<script>", "")
        message = message.replace("</script>", "")
        xss_found = True

    message = sql_pattern.sub("", message)

    if xss_found:
        message += f"\nThis message has been flagged as a potential XSS attack and subsequently cleansed."
    if sql_found:
        message += f"\nThis messages has been flagged as a potential SQL injection and subsequently cleansed."

    return message


def form_message_blocks(message, packet_size, target_public_key):
    # Convert full_message into chunks that are small enough to be encrypted
    # Encrypt each chunk
    # For each encrypted chunk, chunk & pad the result based on packet_size
    full_message = message.form_message()

    if rsa_encrypt(target_public_key, "hello") != rsa_encrypt(get_public_key(), "hello"):
        print("FFFFFFFFFFFFFFFFFFFFFFUCK")
    else:
        print("YYYYYYYYYYYYAAAAAAAAAAAAAAAAAYYYYYYYYYYYYYYYYYY")

    # Convert full_message into chunks that are small enough to be encrypted
    print(f"{type(message)} + {full_message}")
    if type(message) == MessageFile:
        message_as_bytes = full_message
    else:
        message_as_bytes = full_message.encode('utf-8')
    plaintext_chunks = [message_as_bytes[i:i + plaintext_size] for i in range(0, len(full_message), plaintext_size)]

    # Encrypt each chunk
    valid = False
    enc_attempt = 1
    while not valid:
        print(f"Enc attempt {enc_attempt}")
        enc_attempt += 1
        valid = True
        ciphertext_chunks = []
        full_ciphertext = b""
        print(target_public_key)
        for chunk in plaintext_chunks:
            encrypted_chunk = rsa_encrypt(target_public_key, chunk)
            while split_char in encrypted_chunk:
                encrypted_chunk = rsa_encrypt(target_public_key, chunk)
            ciphertext_chunks.append(encrypted_chunk)
        for chunk in ciphertext_chunks:
            #if split_char in chunk:
                #valid = False
            full_ciphertext += chunk
            print(f"Chunk - {chunk}")

    # For each encrypted chunk, chunk & pad the result based on packet_size
    padded_ciphertext_chunks = []
    for chunk in ciphertext_chunks:
        padded_chunks = [chunk[i:i + packet_size] for i in range(0, len(chunk), packet_size)]
        if len(padded_chunks[-1]) < packet_size:
            needed_pad_characters = packet_size - len(padded_chunks[-1])
            padded_chunks[-1] += split_char * needed_pad_characters
        for padded_chunk in padded_chunks:
            padded_ciphertext_chunks.append(padded_chunk)

    yej = b''
    for chunk in padded_ciphertext_chunks:
        if len(chunk) != packet_size:
            for poo in chunk:
                yej += poo
        else:
            yej += chunk

    # Calculate the metadata
    # Convert the metadata into chunks to be encrypted
    # Encrypt each chunk
    # For each encrypted chunk, chunk and pad the result based on packet_size

    # Calculate the metadata
    metadata = (message.target + chr(31) + message.sender + chr(31) + str(message.time_stamp))
    metadata_bytes = metadata.encode('utf-8')

    # Convert the metadata into chunks to be encrypted
    meta_plaintext_chunks = []

    # Encrypt each chunk
    meta_ciphertext_chunks = []

    # For each encrypted chunk, chunk and pad the result based on packet_size
    meta_padded_ciphertext_chunks = [metadata_bytes[i:i + packet_size] for i in
                                     range(0, len(metadata_bytes), packet_size)]
    if len(meta_padded_ciphertext_chunks[-1]) < packet_size:
        needed_pad_characters = packet_size - len(meta_padded_ciphertext_chunks[-1])
        meta_padded_ciphertext_chunks[-1] += b'\x01' * needed_pad_characters

    return padded_ciphertext_chunks, meta_padded_ciphertext_chunks


def decrypt_wrapper(data, type):
    stripped_data = data.replace(split_char, b'')
    ciphertext_chunks = [stripped_data[i:i + ciphertext_size] for i in range(0, len(stripped_data), ciphertext_size)]
    if type == 1:
        plaintext = b""
        for chunk in ciphertext_chunks:
            plaintext += rsa_decrypt(chunk)
    elif type == 2:
        plaintext = b''
        for chunk in ciphertext_chunks:
            plaintext += rsa_decrypt(chunk)
    else:
        print("This is impossible")
        return "An error occurred in decryption"

    return plaintext


class Message:
    def __init__(self, data, target, sender, signature):
        self.data = data
        self.target = target
        self.time_stamp = time.time()
        self.sender = sender
        self.signature = signature

    def __str__(self):
        return f"{self.sender} -> {self.target}\n{self.data}"

    def get_data(self):
        return self.data

    def get_target(self):
        return self.target

    def get_sender(self):
        return self.sender

    def get_signature(self):
        return self.signature

    def form_message(self):
        """
        :param target_public_key: Recipient's RSA public key
        :param server_public_key: Server's RSA public key
        :return: Encrypted string to send to the server
        """
        # TODO cleanse data for SQL & XSS
        #print(self.signature)
        inner_message_plaintext = (self.data + chr(30) + str(self.signature) + chr(30) + self.sender + chr(30) +
                                   str(self.time_stamp) + chr(30) + self.target)

        #print(f"\nInner plaintext - {inner_message_plaintext}")

        return inner_message_plaintext


class MessageFile(Message):
    def __init__(self, file_path, target, sender, signature):
        super().__init__('', target, sender, signature)  # Initialize with empty data; we'll read the file as binary
        self.file_name = file_path
        with open(file_path, "rb") as file:  # Note the "rb" mode here
            self.data = file.read()

    def form_message(self):
        # Preparing the binary message payload
        inner_message_plaintext = (self.data + self.signature + bytes([30]) +
                                   self.sender.encode('utf-8') + bytes([30]) +
                                   str(self.time_stamp).encode('utf-8') + bytes([30]) +
                                   self.file_name.encode('utf-8'))

        inner_message_plaintext = self.data + (str(self.signature) + chr(30) + self.sender + chr(30)
                                               + str(self.time_stamp) + chr(30) + self.file_name).encode('utf-8')

        return inner_message_plaintext
