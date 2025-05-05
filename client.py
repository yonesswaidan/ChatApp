import asyncio
import tkinter as tk
import threading
from common import encrypt_message, decrypt_message

passphrase = None
reader, writer = None, None

async def receive_messages():
    global reader
    while True:
        try:
            data = await reader.read(4096)
            if data:
                message = decrypt_message(passphrase, data)
                print("Server:", message)
            else:
                break
        except Exception as e:
            print("Error:", e)
            break


async def send_messages():
    global writer
    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break
        encrypted = encrypt_message(passphrase, message)
        writer.write(encrypted)
        await writer.drain()
    writer.close()


async def start_client():
    global reader, writer
    reader, writer = await asyncio.open_connection('127.0.0.1', 12345)
    asyncio.create_task(receive_messages())
    await send_messages()


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
    main()
