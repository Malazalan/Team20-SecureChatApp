import time

class Message:
    def __init__(self, data, target, sender, signature):
        self.data = data
        self.target = target
        self.time_stamp = time.time()
        self.sender = sender
        self.signature = signature

    def get_data(self):
        return self.data

    def get_target(self):
        return self.target

    def get_sender(self):
        return self.sender

    def get_signature(self):
        return self.signature

    def form_message_blocks(self, target_public_key, server_public_key):
        #TODO cleanse data for SQL & XSS

        inner_message_plaintext = self.data + self.signature + self.sender
        #TODO encrypt inner_message
        inner_message_ciphertext = inner_message_plaintext

        #TODO sign the inner_message_ciphertext
        inner_message_ciphertext_signature = "TODO_INNER_CIPHERTEXT_SIGNATURE"
        outer_message_plaintext = (inner_message_ciphertext + inner_message_ciphertext_signature + self.sender +
                                   self.target)
        #TODO encrypt outer_message
        outer_message_ciphertext = outer_message_plaintext

        return outer_message_ciphertext
