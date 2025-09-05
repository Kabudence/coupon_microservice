from cryptography.fernet import Fernet

# Generar clave simétrica
key = Fernet.generate_key()
cipher = Fernet(key)

# Tu secreto real (ejemplo)
mp_secret = "TEST-1234567890abcdef"

# Cifrarlo
encrypted = cipher.encrypt(mp_secret.encode())

print("FERNET_KEY =", key.decode())
print("MP_SECRET_ENC =", encrypted.decode())
