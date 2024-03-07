import time


def form_message_blocks(full_message, chunk_size):
    message_as_bytes = full_message.encode('utf-8')
    chunks = [message_as_bytes[i:i+chunk_size] for i in range(0, len(message_as_bytes), chunk_size)]

    if len(chunks[-1]) < chunk_size:
        needed_pad_characters = chunk_size - len(chunks[-1])
        chunks[-1] += b'\x00' * needed_pad_characters  # Assign the padded bytes back to the last chunk

    return chunks


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
        #TODO cleanse data for SQL & XSS

        inner_message_plaintext = self.data + self.signature + self.sender + str(self.time_stamp)
        #TODO encrypt inner_message
        inner_message_ciphertext = inner_message_plaintext

        #TODO sign the inner_message_ciphertext
        inner_message_ciphertext_signature = "TODO_INNER_CIPHERTEXT_SIGNATURE"
        outer_message_plaintext = (inner_message_ciphertext + inner_message_ciphertext_signature + self.sender +
                                   self.target + str(self.time_stamp))
        #TODO encrypt outer_message
        outer_message_ciphertext = outer_message_plaintext

        return outer_message_ciphertext
