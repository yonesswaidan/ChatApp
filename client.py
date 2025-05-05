import asyncio
import tkinter as tk
import threading
import socket
import time
from common import encrypt_message, decrypt_message

def receive_messages(clientSocket, passphrase):
    while True:
        try:
            data = clientSocket.recv(4096)
            if data:
                message = decrypt_message(passphrase, data)
                print("Server:", message)
            else:
                break
            time.sleep(1)
        except Exception as e:
            print("Error:", e)
            break


def send_messages(clientSocket, passphrase):
    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break
        encrypted = encrypt_message(passphrase, message)
        clientSocket.sendall(encrypted)
        time.sleep(1)


def start_client(passphrase):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(('127.0.0.1', 12345))
    in_thread = threading.Thread(target=receive_messages, args=(clientSocket,passphrase))
    out_thread = threading.Thread(target=send_messages, args=(clientSocket,passphrase))
    in_thread.start()
    out_thread.start()

if __name__ == "__main__":
    passphrase = input("What is the passphrase? ")
    start_client(passphrase)
