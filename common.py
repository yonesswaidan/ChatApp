from Crypto.Protocol.KDF import scrypt  # Scrypt, som bruges til at "aflede" en key fra en passphrase

# Funktion til at generere en delt nøgle ud fra en passphrase
def get_shared_key(passphrase):
    salt = b'static_salt'  # Salt er en konstant værdi
    return scrypt(passphrase.encode(), salt, 32, N=2**14, r=8, p=1)
    # scrypt-parametrene betyder:
    # - 32: længden på den nøgle, vi ønsker at aflede
    # - N=2**14, r=8, p=1: disse parametre styrer hvor tungt beregningen er (højere = mere sikker, men langsommere)
