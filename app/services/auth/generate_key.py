import secrets
import base64

def generate_key():
    key = secrets.token_bytes(128)  # Genera 128 bytes de ruido aleatorio
    return base64.b64encode(key).decode('utf-8')     # Lo convierte al string que ves en el XML

if __name__ == "__main__":
    print(generate_key())
