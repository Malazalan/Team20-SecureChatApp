from SocketComms import *
from EncryptionService import *

import os
import queue
import threading
import signal

input_queue = queue.Queue()

sender, target = "", ""

aes_key = os.urandom(32)




def read_input(input_queue):
    while get_keep_running():
        try:
            # Python 2 compatibility: use raw_input() instead of input()
            inp = input()
            input_queue.put(inp)
        except EOFError:
            break


def clear_screen():
    # Check if the operating system is Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Assume any other OS is Unix-based
    else:
        _ = os.system('clear')


def redraw_UI():
    clear_screen()
    for message in messages:
        print(f"{message[2]}\n{message[0]}\n")
    print(f"\n\n\n{sender}:    ")


if __name__ == "__main__":
    if len(sys.argv) != 4:  # Remember, the first arg is the script name itself
        print("Usage: python3 SocketCommsTestUI.py Your username | Their username | Server IP")
        sys.exit(1)

    _, sender, target, server_ip = sys.argv  # Unpack the arguments

    test_multiple_server_ips = ["1.2.3.4", "5.6.7.8", server_ip]

    listen_thread = threading.Thread(target=server_listen_handler, args=(get_private_key(),))
    listen_thread.start()

    input_thread = threading.Thread(target=read_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    signal.signal(signal.SIGINT, signal_handler)

    num_messages = len(messages)
    redraw_UI()

    tempThread = threading.Thread(target=prepare_message, args=(target, sender, "TestImg.jpg", get_public_key(), get_server_public_key(), Message_Type.FILE, test_multiple_server_ips))
    tempThread.start()
    tempThread.join()

    while get_keep_running():
        if len(messages) > num_messages:
            num_messages = len(messages)
            redraw_UI()
        try:
            user_input = input_queue.get_nowait()
            writeThread = threading.Thread(target=prepare_message,
                                           args=(target, sender, user_input, get_public_key(), get_server_public_key(),
                                                 Message_Type.TEXT, test_multiple_server_ips))
            writeThread.start()
            messages.append([user_input, "", sender])
        except queue.Empty:
            pass

        time.sleep(0.1)

    listen_thread.join(timeout=5)  # Timeout in seconds
    if listen_thread.is_alive():
        print("Warning: listen_thread did not terminate gracefully.")
    else:
        print("listen_thread terminated gracefully")
