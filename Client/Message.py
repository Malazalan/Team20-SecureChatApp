import time

from EncryptionService import rsa_encrypt, rsa_decrypt

plaintext_size = 180
ciphertext_size = 256
split_char = b'\x00'

def form_message_blocks(message, packet_size, target_public_key, server_public_key):
    # Convert full_message into chunks that are small enough to be encrypted
    # Encrypt each chunk
    # For each encrypted chunk, chunk & pad the result based on packet_size
    full_message = message.form_message(target_public_key, server_public_key)

    # Convert full_message into chunks that are small enough to be encrypted
    message_as_bytes = full_message.encode('utf-8')
    print(f"{full_message} -> {message_as_bytes}")
    plaintext_chunks = [message_as_bytes[i:i + plaintext_size] for i in range(0, len(full_message), plaintext_size)]
    print(f"Plaintext Chunks -> {plaintext_chunks}")

    # Encrypt each chunk
    valid = False
    while not valid:
        valid = True
        ciphertext_chunks = []
        full_ciphertext = b""
        for chunk in plaintext_chunks:
            ciphertext_chunks.append(rsa_encrypt(target_public_key, chunk))
        for chunk in ciphertext_chunks:
            if split_char in chunk:
                valid = False
            print(f"Ciphertext Chunks -> {chunk}")
            full_ciphertext += chunk

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

    yej2 = yej.replace(split_char, b'')
    print(f"Padded -> \n{yej2}\n{full_ciphertext}")
    if yej2 == full_ciphertext:
        print("\n\n\tHOORAY\n\n")
    else:
        print("\n\n\tFUCKFUCKFUCK\n\n")

    temp = ""
    for thing in yej:
        temp += str(thing)
    print(temp)

    # Calculate the metadata
    # Convert the metadata into chunks to be encrypted
    # Encrypt each chunk
    # For each encrypted chunk, chunk and pad the result based on packet_size

    # fuck encrypting for now
    print("\n\n\n")

    # Calculate the metadata
    metadata = (message.target + chr(31) + message.sender + chr(31) + str(message.time_stamp))
    metadata_bytes = metadata.encode('utf-8')
    print(f"{metadata} -> {metadata_bytes}")

    # Convert the metadata into chunks to be encrypted
    meta_plaintext_chunks = []

    # Encrypt each chunk
    meta_ciphertext_chunks = []

    # For each encrypted chunk, chunk and pad the result based on packet_size
    meta_padded_ciphertext_chunks = [metadata_bytes[i:i + packet_size] for i in range(0, len(metadata_bytes), packet_size)]
    if len(meta_padded_ciphertext_chunks[-1]) < packet_size:
        needed_pad_characters = packet_size - len(meta_padded_ciphertext_chunks[-1])
        meta_padded_ciphertext_chunks[-1] += b'\x01' * needed_pad_characters

    for chunk in meta_padded_ciphertext_chunks:
        print(f"Metadata chunk -> {chunk}")

    return padded_ciphertext_chunks, meta_padded_ciphertext_chunks


def decrypt_wrapper(private_key, data):
    stripped_data = data.replace(split_char, b'')
    ciphertext_chunks = [stripped_data[i:i + ciphertext_size] for i in range(0, len(stripped_data), ciphertext_size)]
    plaintext = ""
    for chunk in ciphertext_chunks:
        print(chunk)
        plaintext += rsa_decrypt(private_key, chunk)

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

    def form_message(self, target_public_key, server_public_key):
        """

        :param target_public_key: Recipient's RSA public key
        :param server_public_key: Server's RSA public key
        :return: Encrypted string to send to the server
        """
        # TODO cleanse data for SQL & XSS
        self.signature = "TODO_INNER_SIGNATURE"
        inner_message_plaintext = (self.data + chr(30) + self.signature + chr(30) + self.sender + chr(30) +
                                   str(self.time_stamp))

        print(f"\nInner plaintext - {inner_message_plaintext}")

        return inner_message_plaintext
