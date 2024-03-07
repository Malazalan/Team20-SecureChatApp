import socket
import threading
import signal
import sys
import time
from Message import *

MAX_PACKET_LENGTH = 128
server_ip = "127.0.0.1"
server_port = 54321

keepRunning = True  # Flag to control the execution flow
stdout_mutex = threading.Lock()
socket_mutex = threading.Lock()


def signal_handler(sig, frame):
    global keepRunning
    with stdout_mutex:
        print("Ctrl+C received, killing threads...")
    keepRunning = False


def server_listen_handler():
    global keepRunning
    #while keepRunning:
        #with stdout_mutex:
            #print("Listener thread ... waiting for a job")
        #time.sleep(3)


def server_send_handler(message_to_send):
    with socket_mutex:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((server_ip, server_port))

        # Tell the server to expect len(message_to_send) chunks
        # len(message_to_send) should be an integer turned into bytes that is exactly MAX_PACKET_LENGTH bytes long
        message_length = len(message_to_send).to_bytes(MAX_PACKET_LENGTH, byteorder='little')
        server.send(message_length)

        for message in message_to_send:
            server.send(message)
        server.close()


def prepare_message(sender, target, data, target_public_key, server_public_key):
    message_signature = "ADD THE SIGNATURE STUFF"
    message_to_send = Message(data, target, sender, "")

    full_message_to_send = message_to_send.form_message(target_public_key, server_public_key)

    bytes_full_message_to_send = form_message_blocks(full_message_to_send, MAX_PACKET_LENGTH)

    server_send_handler(bytes_full_message_to_send)


if __name__ == '__main__':
    # System initialisation
    signal.signal(signal.SIGINT, signal_handler)

    listenThread = threading.Thread(target=server_listen_handler)
    listenThread.start()

    # Security initialisation

    # Test stuff
    while keepRunning:
        writeThread = threading.Thread(target=prepare_message, args=("Alice", "Bob", f"This is a long message!\n\nI'm even including weird variables to make it harder to parse and send!", "", ""))
        writeThread.start()
        time.sleep(5)

    listenThread.join()
    print("Program terminated gracefully")
