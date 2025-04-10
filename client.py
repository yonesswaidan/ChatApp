import asyncio
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

async def communicate():
    shared_key = scrypt(b"my_shared_secret", b"salt", 32, N=2**14, r=8, p=1)

    reader, writer = await asyncio.open_connection('localhost', 12345)
    print("Connected to server")

    while True:
        message = input("Enter message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break

        encrypted_message = encrypt_message(shared_key, message)
        writer.write(encrypted_message)
        await writer.drain()

        data = await reader.read(1024)
        if data:
            response = decrypt_message(shared_key, data)
            print(f"Server says: {response}")
        else:
            print("No response from server.")

    print("Closing connection")
    writer.close()

asyncio.run(communicate())
