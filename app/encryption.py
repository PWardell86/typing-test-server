import binascii
import hashlib
import secrets

def get_salt_hash(password):
    salt = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt, binascii.hexlify(key).decode('utf-8')

def valid_password(password, salt, hash):
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return binascii.hexlify(key).decode('utf-8') == hash
