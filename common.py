from Crypto.Protocol.KDF import scrypt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def derive_key(passphrase, salt):
    return scrypt(passphrase.encode(), salt, 32, N=2**14, r=8, p=1)

def encrypt_message(passphrase, message):
    salt = get_random_bytes(16)
    key = derive_key(passphrase, salt)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return salt + nonce + tag + ciphertext



def decrypt_message(passphrase, encrypted_data):
    salt = encrypted_data[:16]
    nonce = encrypted_data[16:28]
    tag = encrypted_data[28:44]
    ciphertext = encrypted_data[44:]
    key = derive_key(passphrase, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
