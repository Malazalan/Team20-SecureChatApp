import select
import socket
import threading
import signal
import sys
import time
from Message import *
from Header import *

MAX_PACKET_LENGTH = 12
MAX_RECONN = 15
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

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(("0.0.0.0", 12345))
    listen_socket.listen(10)

    if not listen_socket:
        print("Listen socket failed to start")
        keepRunning = False
    while keepRunning:
        ready_to_read, _, _ = select.select([listen_socket], [], [], 1)  # Timeout set to 1 second
        if listen_socket in ready_to_read:
            print("Ready to read")
            server_socket, _ = listen_socket.accept()
            print("Client accepted")
            header = bytes_to_header(server_socket.recv(HEADER_LENGTH, 0))
            print(f"Header:\nType - {header.type}\nPackets - {header.number_of_packets}")
            message = b""
            for packet_num in range(0, header.number_of_packets):
                packet = server_socket.recv(MAX_PACKET_LENGTH, 0)
                message += packet
            print(message.decode('utf-8'))
        else:
            if not keepRunning:
                break

    listen_socket.close()



def server_send_handler(message_to_send, message_type):
    with socket_mutex:
        attempts = 1
        while attempts < MAX_RECONN:
            sent = True
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(1)
            try:
                print(f"Connecting to server")
                server.connect((server_ip, server_port))

                # Tell the server to expect len(message_to_send) chunks
                # len(message_to_send) should be an integer turned into bytes that is exactly MAX_PACKET_LENGTH bytes long
                message_header = Header(message_type, len(message_to_send))

                message_length = len(message_to_send).to_bytes(MAX_PACKET_LENGTH, byteorder='little')
                #server.send(message_length)
                print(f"Sending header")
                server.send(message_header.get_header_bytes())

                count = 1
                for message in message_to_send:
                    count += 1
                    server.send(message)
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



def prepare_message(sender, target, data, target_public_key, server_public_key, message_type):
    message_signature = "ADD THE SIGNATURE STUFF"
    message_to_send = Message(data, target, sender, "")

    full_message_to_send = message_to_send.form_message(target_public_key, server_public_key)

    bytes_full_message_to_send = form_message_blocks(full_message_to_send, MAX_PACKET_LENGTH)

    server_send_handler(bytes_full_message_to_send, message_type)


if __name__ == '__main__':
    # System initialisation
    listenThread = threading.Thread(target=server_listen_handler)
    listenThread.start()


    signal.signal(signal.SIGINT, signal_handler)

    # Security initialisation

    # Test stuff
    # Text test
    writeThread = threading.Thread(target=prepare_message, args=("Alice", "Alice", f"Data", "", "", Message_Type.TEXT))
    writeThread.start()

    listenThread.join()
    print("Program terminated gracefully")
