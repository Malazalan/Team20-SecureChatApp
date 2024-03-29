import ast
import base64
import binascii
import select
import socket
import threading
import signal
import sys
import time

import socketio
from EncryptionService import   rsa_decrypt, get_private_key, get_public_key, sign, verify_signature
from Message import *
from Header import *
from Database import get_public_key_from_user, get_user

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


def server_listen_handler(private_key, socketio):
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
            print("Server accepted")
            message_header = bytes_to_header(server_socket.recv(HEADER_LENGTH, 0))
            metadata_header = bytes_to_header(server_socket.recv(HEADER_LENGTH, 0))
            file_metadata_header = None
            if message_header.type == Message_Type.FILE.value:
                file_metadata_header = bytes_to_header(server_socket.recv(HEADER_LENGTH, 0))
            print(f"Message header:\nType - {message_header.type}\nPackets - {message_header.number_of_packets}\n")
            print(f"Metadata header:\nType - {metadata_header.type}\nPackets - {metadata_header.number_of_packets}\n")
            if file_metadata_header:
                print(f"File metadata header:\nType - {file_metadata_header.type}\nFile size - {file_metadata_header.number_of_packets}\n")
            message = b""
            for packet_num in range(0, message_header.number_of_packets):
                packet = server_socket.recv(MAX_PACKET_LENGTH, 0)
                message += packet

            if message_header.type == Message_Type.TEXT.value:
                temp = decrypt_wrapper(message, message_header.type)
                split_message = decrypt_wrapper(message, message_header.type).decode('utf-8').split(chr(30))
                bytes_signature = ast.literal_eval(split_message[1])
                split_message[2] += f" - {verify_signature(get_public_key_from_user(split_message[2]), split_message[0].encode('utf-8'), bytes_signature)}"

                data = {
                    "username": split_message[2],
                    "target": split_message[4],
                    "message": split_message[0],
                    "is_encrypted": False
                }

                target = get_user(split_message[4])
                print(target)
                target_room = target.current_room
                socketio.emit('receive_message', data, room=target_room)
                print("Yay??")

            elif message_header.type == Message_Type.FILE.value:
                decrypted_message = decrypt_wrapper(message, message_header.type)
                file_data = decrypted_message[:file_metadata_header.number_of_packets]

                remaining_data = decrypted_message[file_metadata_header.number_of_packets:]

                split_message = remaining_data.decode('utf-8').split(chr(30))

                bytes_signature = ast.literal_eval(split_message[0])

                file_name_with_verification = str(
                    verify_signature(get_public_key_from_user(split_message[1]), file_data, bytes_signature)
                ) + " - " + split_message[3]

                print(f"File bytes recv {file_data}")

                data = {
                    'username': split_message[1],
                    'target': split_message[4],
                    'fileData': file_data,
                    'fileName': file_name_with_verification
                }
                target = get_user(split_message[4])
                print(target)
                target_room = target.current_room
                socketio.emit('receive_file', data, room=target_room)
                print("Yay file??")
            else:
                print("This should not be possible")
        else:
            if not keepRunning:
                break

    listen_socket.close()


def server_send_handler(message_to_send, metadata_to_send, message_type, server_ips, message):
    finished_sending = False
    with socket_mutex:
        for server_ip in server_ips:
            if finished_sending:
                break

            print(f"Connecting to server {server_ip}:{server_port}")
            attempts = 1
            while attempts < MAX_RECONN:
                sent = True
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.settimeout(1)
                try:
                    server.connect((server_ip, server_port))

                    # Tell the server to expect len(message_to_send) chunks
                    message_header = Header(message_type, len(message_to_send))
                    server.send(message_header.get_header_bytes())

                    metadata_header = Header(Message_Type.METADATA, len(metadata_to_send))
                    server.send(metadata_header.get_header_bytes())

                    if message_header.type == Message_Type.FILE:
                        file_metadata_header = Header(Message_Type.METADATA, len(message.data))
                        server.send(file_metadata_header.get_header_bytes())

                    count = 0
                    for message in message_to_send:
                        count += 1
                        #print(message)
                        server.send(message)
                    print(f"Message sent\n")

                    count = 0
                    for metadata in metadata_to_send:
                        count += 1
                        server.send(metadata)
                        #print(f"Sent metadata {count}/{len(metadata_to_send)}")
                    print(f"Metadata sent\n")

                    finished_sending = True
                except socket.timeout:
                    print(f"Retry {attempts}/{MAX_RECONN}")
                    sent = False
                except Exception as e:
                    print(f"Uncaught exception {e}")
                finally:
                    server.close()
                    if attempts > MAX_RECONN or sent:
                        if not sent:
                            print(f"Connection timed out")
                        break
                    else:
                        attempts += 1


def prepare_message(sender, target, data, target_public_key, message_type, server_ips, file_name=None):
    if message_type == Message_Type.TEXT:
        #print(f"\tData 1 - {data.encode('utf-8')}")
        message_signature = sign(data.encode('utf-8'))
        message_to_send = Message(data, target, sender, message_signature)

        message, metadata = form_message_blocks(message_to_send, MAX_PACKET_LENGTH, target_public_key)
    elif message_type == Message_Type.FILE:
        #with open(data, mode="rb") as file:
            #file_bytes = file.read()
        #print(f"Data 1 - {file_bytes}")
        file_bytes = data
        message_signature = sign(file_bytes)
        while bytes([30]) in message_signature:
            message_signature = sign(file_bytes)
        #print(message_signature)
        message_to_send = MessageFile(file_name, data, target, sender, message_signature)

        message, metadata = form_message_blocks(message_to_send, MAX_PACKET_LENGTH, target_public_key)
    else:
        print(f"Invalid type - {message_type}")
        return
    server_send_handler(message, metadata, message_type, server_ips, message_to_send)


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
