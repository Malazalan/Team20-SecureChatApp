import os
from SocketComms import *
import queue
import threading
import signal

input_queue = queue.Queue()

sender, target = "", ""


def signal_handler(sig, frame):
    global keepRunning
    with stdout_mutex:
        print("Ctrl+C received, killing threads...")
    keepRunning = False


def read_input(input_queue):
    while keepRunning:
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
        print(f"{message[2]}:    {message[0]}")
    print(f"\n\n\n{sender}:    ")



if __name__ == "__main__":
    keepRunning = True
    if len(sys.argv) != 4:  # Remember, the first arg is the script name itself
        print("Usage: python3 SocketCommsTestUI.py Your username | Their username | Server IP")
        sys.exit(1)

    _, sender, target, server_ip = sys.argv  # Unpack the arguments

    listen_thread = threading.Thread(target=server_listen_handler)
    listen_thread.start()

    input_thread = threading.Thread(target=read_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    signal.signal(signal.SIGINT, signal_handler)

    num_messages = len(messages)
    redraw_UI()
    while keepRunning:
        if len(messages) > num_messages:
            num_messages = len(messages)
            redraw_UI()
        try:
            user_input = input_queue.get_nowait()
            writeThread = threading.Thread(target=prepare_message, args=(sender, target, user_input, "", "", Message_Type.TEXT))
            writeThread.start()
            messages.append([user_input, "", sender])
        except queue.Empty:
            pass

        time.sleep(0.1)

    listen_thread.join()
