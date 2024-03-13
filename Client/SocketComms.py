import binascii
import select
import socket
import threading
import signal
import sys
import time

from EncryptionService import rsa_decrypt, get_private_key
from Message import *
from Header import *

MAX_PACKET_LENGTH = 256
MAX_RECONN = 15
# server_ip = "194.164.20.210"
# server_ip = "127.0.0.1"
server_port = 54321

keepRunning = True  # Flag to control the execution flow
stdout_mutex = threading.Lock()
socket_mutex = threading.Lock()

messages = []


def hex_print(data):
    print(binascii.hexlify(data))


def set_keep_running(status):
    global keepRunning
    keepRunning = status


def get_keep_running():
    return keepRunning


def signal_handler(sig, frame):
    global keepRunning
    with stdout_mutex:
        print("Ctrl+C received, killing threads...")
    keepRunning = False


def server_listen_handler(private_key):
    global keepRunning

    print("Starting listener")

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(("0.0.0.0", 12345))
    listen_socket.listen(10)
    listen_socket.settimeout(2)

    if not listen_socket:
        print("Listen socket failed to start")
        keepRunning = False
    while keepRunning:
        ready_to_read, _, _ = select.select([listen_socket], [], [], 1)  # Timeout set to 1 second
        if listen_socket in ready_to_read:
            print("Ready to read")
            server_socket, _ = listen_socket.accept()
            print("Client accepted")
            message_header = bytes_to_header(server_socket.recv(HEADER_LENGTH, 0))
            metadata_header = bytes_to_header(server_socket.recv(HEADER_LENGTH, 0))
            print(f"Message header:\nType - {message_header.type}\nPackets - {message_header.number_of_packets}")
            print(f"Metadata header:\nType - {metadata_header.type}\nPackets - {metadata_header.number_of_packets}\n")
            message = b""
            for packet_num in range(0, message_header.number_of_packets):
                packet = server_socket.recv(MAX_PACKET_LENGTH, 0)
                message += packet

            messages.append(decrypt_wrapper(private_key, message).split(chr(30)))
        else:
            if not keepRunning:
                break

    listen_socket.close()


def server_send_handler(message_to_send, metadata_to_send, message_type, server_ip):
    with socket_mutex:
        attempts = 1
        while attempts < MAX_RECONN:
            sent = True
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(1)
            try:
                print(f"Connecting to server {server_ip}:{server_port}")
                server.connect((server_ip, server_port))

                # Tell the server to expect len(message_to_send) chunks
                message_header = Header(message_type, len(message_to_send))
                message_length = len(message_to_send).to_bytes(MAX_PACKET_LENGTH, byteorder='little')
                # server.send(message_length)
                server.send(message_header.get_header_bytes())

                metadata_header = Header(Message_Type.METADATA, len(metadata_to_send))
                print(metadata_header.get_header_bytes())
                server.send(metadata_header.get_header_bytes())

                count = 0
                for message in message_to_send:
                    count += 1
                    server.send(message)
                    print(f"Sent message {count}/{len(message_to_send)}")
                print(f"Message sent\n")

                count = 0
                for metadata in metadata_to_send:
                    count += 1
                    server.send(metadata)
                    print(f"Sent metadata {count}/{len(metadata_to_send)}")
                print(f"Metadata sent\n")
            except socket.timeout:
                print(f"Retry {attempts}/{MAX_RECONN}")
                sent = False
            finally:
                server.close()
                if attempts > MAX_RECONN or sent:
                    if not sent:
                        print(f"Connection timed out")
                    break
                else:
                    attempts += 1


def prepare_message(sender, target, data, target_public_key, server_public_key, message_type, server_ip):
    message_signature = "ADD THE SIGNATURE STUFF"
    message_to_send = Message(data, target, sender, "")

    message, metadata = form_message_blocks(message_to_send, MAX_PACKET_LENGTH, target_public_key, server_public_key)

    server_send_handler(message, metadata, message_type, server_ip)


if __name__ == '__ain__':
    # System initialisation
    listenThread = threading.Thread(target=server_listen_handler)
    listenThread.start()

    signal.signal(signal.SIGINT, signal_handler)

    # Security initialisation

    # Test stuff
    # Text test
    writeThread = threading.Thread(target=prepare_message,
                                   args=("John", "Alan", f"Hello World!", "", "", Message_Type.TEXT))
    writeThread.start()

    listenThread.join()
    print("Program terminated gracefully")
