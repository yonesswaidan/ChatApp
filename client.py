import asyncio
import tkinter as tk
import threading
import socket
import time
from common import encrypt_message, decrypt_message

passphrase = None

def receive_messages(clientSocket):
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


def send_messages(clientSocket):
    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break
        encrypted = encrypt_message(passphrase, message)
        clientSocket.sendall(encrypted)
        time.sleep(1)


async def start_client():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(('127.0.0.1', 12345))
    in_thread = threading.Thread(target=receive_messages, args=(clientSocket,))
    out_thread = threading.Thread(target=send_messages, args=(clientSocket,))
    in_thread.start()
    out_thread.start()

def main():
    def on_connect():
        global passphrase
        user_input = entry.get()
        if not user_input:
            error_label.config(text="Please enter a passphrase.")
        else:
            passphrase = user_input
            error_label.config(text="Connected. Write in terminal.")
            connect_button.config(state=tk.DISABLED)
            threading.Thread(target=lambda: asyncio.run(start_client())).start()

    root = tk.Tk()
    root.title("Client")
    tk.Label(root, text="Enter passphrase:").pack(pady=10)
    entry = tk.Entry(root, show="*")
    entry.pack(pady=5)
    connect_button = tk.Button(root, text="Connect", command=on_connect)
    connect_button.pack(pady=10)
    error_label = tk.Label(root, text="", fg="red")
    error_label.pack()
    root.mainloop()

if __name__ == "__main__":
    passphrase = "test"
    asyncio.run(start_client())
