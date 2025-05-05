import asyncio
import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

passphrase = None  # Gemmes passphrasen

# Funktion der finde en key ud fra passphrasen
def get_shared_key(passphrase):
    salt = b'static_salt'  # Salt bruges for at gøre det "sværere" for black-hat hacker
    return scrypt(passphrase.encode(), salt, 32, N=2**14, r=8, p=1)

# Funktion til kryption af beskeder
def encrypt_message(key, message):
    nonce = get_random_bytes(12)  # Nonce (engangsnummer som nævnt i README.md)(Hjælper med at gøre den unik)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # AES-GCM kryptering
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())  # Krypter beskeden og få en authen tag
    return nonce + tag + ciphertext  # Retuner krypteret besked med nonce og tag

# Funktion til at dekryptere beskeder
def decrypt_message(key, encrypted_message):
    nonce, tag, ciphertext = encrypted_message[:12], encrypted_message[12:28], encrypted_message[28:]  # funktion omdeller krypteret besked
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # AES-GCM til dekryptering
    return cipher.decrypt_and_verify(ciphertext, tag).decode()  # Dekrypter og tjek om det er autenstisk

# Funktion til at kommunikere med serveren
async def communicate():
    global passphrase
    if passphrase is None:  # Tjek at passphrasen er sat
        messagebox.showerror("Error", "You must enter a passphrase.")
        return

    key = get_shared_key(passphrase)  # "Afledder" krypteringsnøgle fra passphrasen
    reader, writer = await asyncio.open_connection('127.0.0.1', 12345)  # Opretter forbindelse til serveren

    while True:
        message = input("You: ")  # Brugeren skriver en besked
        if message.lower() == "exit":  # Hvis brugeren skriver "exit", afslutter kommunikationen
            break
        writer.write(encrypt_message(key, message))  # Kryptere beskeden og sender den
        await writer.drain()  # Vent på at beskeden bliver sendt

        data = await reader.read(1024)  # Læser svar fra serveren
        if data:
            print("Server:", decrypt_message(key, data))  # Dekrypter og viser serverens besked

    writer.close()  # Luk forbindelsen til serveren

# Funktion til at starte kommunikationen, kaldt fra UI
def start_communicate():
    global passphrase
    passphrase = passphrase_entry.get()  # Hent passphrasen fra inputfeltet

    if not passphrase:  # Hvis der ikke er angivet passphrase
        messagebox.showerror("Error", "Passphrase cannot be empty")
        return

    asyncio.run(communicate())  # Starter kommunikationen async

# Funktion til at opsætte og starte UI
def start_client_ui():
    global passphrase_entry

    root = tk.Tk()  # Opret et Tkinter vindue
    root.title("Client")  # Sætter vinduets titel

    label = tk.Label(root, text="Enter passphrase:")  # Label for passphrase input
    label.pack(pady=10) 

    passphrase_entry = tk.Entry(root, show="*")  # Skjuler tegnene
    passphrase_entry.pack(pady=10)  

    connect_button = tk.Button(root, text="Connect", command=start_communicate)  # Knapp til at starte kommunikationen
    connect_button.pack(pady=20) 

    root.mainloop()  

if __name__ == "__main__":  
    start_client_ui()  
