import asyncio
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import os

def encrypt_message(key, message):
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return nonce + tag + ciphertext

def decrypt_message(key, encrypted_message):
    nonce, tag, ciphertext = encrypted_message[:12], encrypted_message[12:28], encrypted_message[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        message = cipher.decrypt_and_verify(ciphertext, tag)
        return message.decode()
    except ValueError:
        raise ValueError("Invalid decryption or integrity check failed!")

async def handle_client(reader, writer):
    shared_key = scrypt(b"my_shared_secret", b"salt", 32, N=2**14, r=8, p=1)
    print("New client connected")

    while True:
        try:
            data = await reader.read(1024)
            if not data:
                break

            message = decrypt_message(shared_key, data)
            print(f"Received message: {message}")

            response = f"Echo: {message}"
            encrypted_response = encrypt_message(shared_key, response)
            writer.write(encrypted_response)
            await writer.drain()

        except Exception as e:
            print(f"Error: {e}")
            break

    print("Closing connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 12345)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()

asyncio.run(main())
