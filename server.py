import asyncio
import tkinter as tk
from common import decrypt_message, encrypt_message

clients = set()
passphrase = None


async def handle_client(reader, writer):
    global passphrase
    clients.add(writer)
    addr = writer.get_extra_info('peername')
    print(f"Client {addr} connected")

    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            try:
                print("Broadcasting message")
                for client in clients:
                    if client != writer:
                        client.write(data)
                        await client.drain()
            except Exception as e:
                print(f"Failed to decrypt from {addr}: {e}")
                break
    finally:
        print(f"Client {addr} disconnected")
        clients.remove(writer)
        writer.close()


async def start_server():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 12345)
    print("Server running on 127.0.0.1:12345")
    async with server:
        await server.serve_forever()


def main():
    def on_start():
        global passphrase
        user_input = entry.get()
        if not user_input:
            error_label.config(text="Please enter a passphrase.")
        else:
            passphrase = user_input
            start_button.config(state=tk.DISABLED)
            error_label.config(text="Server is running.")
            asyncio.run(start_server())

    root = tk.Tk()
    root.title("Server")
    tk.Label(root, text="Enter passphrase:").pack(pady=10)
    entry = tk.Entry(root, show="*")
    entry.pack(pady=5)
    start_button = tk.Button(root, text="Start Server", command=on_start)
    start_button.pack(pady=10)
    error_label = tk.Label(root, text="", fg="red")
    error_label.pack()
    root.mainloop()

if __name__ == "__main__":
    passphrase = "test"
    asyncio.run(start_server())
