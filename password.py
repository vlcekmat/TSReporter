from cryptography.fernet import Fernet
from config import write_config, read_config


def get_password():
    saved_password = read_config("s_password")
    if saved_password == "":
        return saved_password
    else:
        password = decrypt_password(saved_password)
        return password


def save_password(password):
    password_to_save = encrypt_password(password)
    write_config("s_password", password_to_save)


def encrypt_password(password_to_encrypt):
    key = b'BCvaDwExib_K-UThnPHIFjBJbjrdv-oD8ZNH5UDy0Sk='
    f = Fernet(key)
    encrypted_password = f.encrypt(password_to_encrypt.encode())
    return encrypted_password.decode()


def decrypt_password(password_to_decrypt):
    key = b'BCvaDwExib_K-UThnPHIFjBJbjrdv-oD8ZNH5UDy0Sk='
    f = Fernet(key)
    decrypted = f.decrypt(password_to_decrypt.encode()).decode()
    return decrypted


