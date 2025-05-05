import asyncio
import tkinter as tk
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

# Funktion til at "aflede" en key ud fra passphrasen
def get_shared_key(passphrase):
    salt = b'static_salt'  # Salt er en konstant værdi(sikker)
    return scrypt(passphrase.encode(), salt, 32, N=2**14, r=8, p=1)  # scrypt bruges til at generere en sikker key

# Funktion til at kryptere en besked med AES
def encrypt_message(key, message):
    nonce = get_random_bytes(12)  # Nonce (engangsnummer)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # Bruger AES-GCM til kryptering
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())  # Krypter beskeden og få en authen tag
    return nonce + tag + ciphertext  # Retunere krypteret besked med nonce og tag

# Funktion til at dekryptere en besked med AES
def decrypt_message(key, encrypted_message):
    nonce, tag, ciphertext = encrypted_message[:12], encrypted_message[12:28], encrypted_message[28:]  # Opdeller krypteret besked
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # Bruger AES-GCM til dekryptering
    return cipher.decrypt_and_verify(ciphertext, tag).decode()  # Dekrypter og tjekker om beskeden er autentisk

# Funktion til at håndtere kommunikation med en klient
async def handle_client(reader, writer, key):
    print("Client connected")  # Print når klienten tilslutter sig("Ikke ens betydende med passphrase er skrevet korrekt")

    while True:
        try:
            data = await reader.read(1024)  # Læs data fra klienten
            if not data:  # Hvis der ikke er data, betyder det at klienten har afsluttet forbindelsen eller ikke har skrevet den rigtige passphrase
                break

            message = decrypt_message(key, data)  # Dekrypter beskeden
            print(f"Received: {message}")  # Printer den modtagne besked

            response = f"Echo: {message}"  # Lav et svar, der gentager beskeden
            writer.write(encrypt_message(key, response))  # Krypter svaret og sender det tilbage
            await writer.drain()  # Sørg for at svaret bliver sendt

        except Exception as e:  
            print(f"Error: {e}")
            break

    writer.close() 

# Funktion til at starte serveren og håndtere klientforbindelser
async def main(passphrase):
    key = get_shared_key(passphrase)  # Afled key fra passphrasen
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, key), '127.0.0.1', 12345)  # Start serveren
    print("Server running on 127.0.0.1:12345")  # Serveren kører på denne IP og port
    async with server:
        await server.serve_forever()  # Bliver ved med at kører

# Funktion til at starte serveren og håndtere eventuelle fejl
def start_server(passphrase):
    try:
        asyncio.run(main(passphrase))  # Start serveren asynkront
    except Exception as e:
        print(f"Error starting server: {e}") 

# Funktion til at opsætte og UI til serveren
def start_server_ui():
    def on_start_button_click():
        passphrase = passphrase_entry.get()  # Henter passphrasen fra inputfeltet
        if passphrase:  # Hvis passphrasen er angivet
            start_server(passphrase)  # Start serveren
            info_label.config(text="Server is running. Waiting for clients...")  # Opdater GUI'en med besked om serverstatus
            start_button.config(state=tk.DISABLED)  # Deaktiver startknappen, hvis serveren den kørere
        else:  
            error_label.config(text="Please enter a passphrase.") 

    root = tk.Tk()  # Opret et Tkinter vindue
    root.title("Server")  # Sæt vinduets titel

    passphrase_label = tk.Label(root, text="Enter passphrase:")  # Label for pssphrase
    passphrase_label.pack(pady=10)  

    passphrase_entry = tk.Entry(root, show="*")  # Skjul tegnene for passphrase
    passphrase_entry.pack(pady=5)  

    start_button = tk.Button(root, text="Start Server", command=on_start_button_click)  # Knapp til at starte serveren
    start_button.pack(pady=10) 

    info_label = tk.Label(root, text="Waiting for client...")  # serverstatus
    info_label.pack(pady=5) 

    error_label = tk.Label(root, text="", fg="red")  
    error_label.pack(pady=5)  

    root.mainloop()  # Start Tkinter event loop, så GUI vises

if __name__ == "__main__":
    start_server_ui()  # Start serverens GUI
