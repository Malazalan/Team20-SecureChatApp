import socket
import threading
import signal
import sys
import time
from Message import *

MAX_PACKET_LENGTH = 64

keepRunning = True  # Flag to control the execution flow
stdout_mutex = threading.Lock()


def signal_handler(sig, frame):
    global keepRunning
    with stdout_mutex:
        print("Ctrl+C received, killing threads...")
    keepRunning = False


def server_listen_handler():
    global keepRunning
    while keepRunning:
        with stdout_mutex:
            print("Listener thread ... waiting for a job")
        time.sleep(3)


def server_send_handler(message_to_send):
    with stdout_mutex:
        print(message_to_send)


def prepare_message(sender, target, data, target_public_key, server_public_key):
    message_signature = "ADD THE SIGNATURE STUFF"
    message_to_send = Message(data, target, sender, "")

    full_message_to_send = message_to_send.form_message(target_public_key, server_public_key)

    bytes_full_message_to_send = form_message_blocks(full_message_to_send, MAX_PACKET_LENGTH)

    with stdout_mutex:
        print(message_to_send)
        print(full_message_to_send)
        print(bytes_full_message_to_send)
        print(len(bytes_full_message_to_send[-1]))


if __name__ == '__main__':
    # System initialisation
    signal.signal(signal.SIGINT, signal_handler)

    listenThread = threading.Thread(target=server_listen_handler)
    listenThread.start()

    # Security initialisation

    # Test stuff
    prepare_message("Alan", "Joe", "Test message!", "", "")

    listenThread.join()
    print("Program terminated gracefully")
