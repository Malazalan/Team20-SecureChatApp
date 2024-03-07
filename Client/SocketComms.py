import socket
import threading
import signal
import sys
import time

keepRunning = True  # Flag to control the execution flow


def signal_handler(sig, frame):
    global keepRunning
    print("Ctrl+C received, killing threads...")
    keepRunning = False


def server_listen_handler():
    global keepRunning
    while keepRunning:
        print("Listener thread... waiting for a job")
        time.sleep(3)


def server_send_handler():
    global keepRunning
    while keepRunning:
        #Write thread


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    listenThread = threading.Thread(target=server_listen_handler)
    listenThread.start()

    while keepRunning:
        print("Main thread: Waiting for SIGINT...")
        time.sleep(2)

    listenThread.join()
    print("Program terminated gracefully")
