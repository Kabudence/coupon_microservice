# ppp.py
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()  # Carga MP_SECRET_ENC desde .env

enc = os.getenv("MP_SECRET_ENC")
key = os.environ.get("FERNET_KEY")  # de variable de entorno del SO

if not enc:
    raise SystemExit("Falta MP_SECRET_ENC en .env")
if not key:
    raise SystemExit("Falta FERNET_KEY en variables de entorno del sistema")

try:
    secret = Fernet(key).decrypt(enc.encode()).decode()
    print("✅ Secreto desencriptado OK:", secret)
except Exception as e:
    print("❌ Error desencriptando:", e)
