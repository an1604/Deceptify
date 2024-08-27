import os
import traceback
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from dotenv import load_dotenv

load_dotenv()


def debug_info():
    """Utility function to print debug information."""
    print("Debug info:")
    print(f"Current directory: {os.getcwd()}")
    print(f"Environment variables: {os.environ}")


def get_key(key_filename):
    try:
        secret_code = os.getenv('SERVER_SECRET_KET')
        if not secret_code:
            raise ValueError("SERVER_SECRET_KET environment variable is not set.")

        with open(key_filename, 'rb') as f:
            encrypted_key = f.read()

        key = RSA.import_key(encrypted_key, passphrase=secret_code)
        return key
    except Exception as e:
        print(f"Exception occurred in get_key: {e}")
        debug_info()
        traceback.print_exc()


def generate_rsa_keypair(key_filename):
    try:
        secret_code = os.getenv('SERVER_SECRET_KET')
        if not secret_code:
            raise ValueError("SERVER_SECRET_KET environment variable is not set.")

        key = RSA.generate(2048)
        encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
                                       protection="scryptAndAES128-CBC",
                                       prot_params={'iteration_count': 131072})

        with open(key_filename, 'wb') as f:
            f.write(encrypted_key)

        print(key.publickey().export_key())
    except Exception as e:
        print(f"Exception occurred in generate_rsa_keypair: {e}")
        debug_info()
        traceback.print_exc()


def get_rsa_keypair(key_filename):
    try:
        key = get_key(key_filename)
        if key:
            print(key.publickey().export_key())
        return key
    except Exception as e:
        print(f"Exception occurred in get_rsa_keypair: {e}")
        debug_info()
        traceback.print_exc()


def save_both_keys(key_filename):
    try:
        key = get_key(key_filename)
        if not key:
            raise ValueError("Failed to retrieve the RSA key pair.")

        private_key = key.export_key()
        private_key_filename = f'{key_filename}-private.pem'

        with open(private_key_filename, 'wb') as f:
            f.write(private_key)
            print(f'{private_key_filename} saved.')

        public_key = key.publickey().export_key()
        public_key_filename = f'{key_filename}-public.pem'

        with open(public_key_filename, 'wb') as f:
            f.write(public_key)
            print(f'{public_key_filename} saved.')

        return private_key_filename, public_key_filename
    except Exception as e:
        print(f"Exception occurred in save_both_keys: {e}")
        debug_info()
        traceback.print_exc()


def encrypt_message(message, public_key_filename):
    try:
        public_key = RSA.import_key(open(public_key_filename, 'rb').read())
        session_key = get_random_bytes(16)

        cipher = PKCS1_OAEP.new(public_key)
        enc_session_key = cipher.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(message)

        return enc_session_key, cipher_aes.nonce, tag, ciphertext

    except Exception as e:
        print(f"Exception occurred in encrypt_message: {e}")
        debug_info()
        traceback.print_exc()


def decrypt_message(enc_session_key, nonce, tag, ciphertext, private_key_filename):
    try:
        private_key = RSA.import_key(open(private_key_filename).read())

        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data.decode('utf-8')
    except Exception as e:
        print(f"Exception occurred in decrypt_message: {e}")
        debug_info()
        traceback.print_exc()
