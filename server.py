import asyncio
import tkinter as tk
from common import decrypt_message, encrypt_message

clients = set()


async def handle_client(reader, writer):
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

if __name__ == "__main__":
    asyncio.run(start_server())
