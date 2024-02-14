import hashlib
import binascii
import secrets
import jwt
import datetime
from flask import request

def get_json(request, *args):
    try:
        data = request.get_json()
        return [data.get(arg) for arg in args]
    except Exception as e:
        return None
        
def get_salt_hash(password):
    salt = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt, binascii.hexlify(key).decode('utf-8')

def valid_password(password, salt, hash):
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return binascii.hexlify(key).decode('utf-8') == hash

def get_token(username, secret_key):
    return jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, secret_key)
    
def is_token_valid(token, secret_key):
    try:
        token_data = jwt.decode(token.encode('utf-8'), secret_key, algorithms=["HS256"])
        return token_data['exp'] > datetime.datetime.utcnow()
    except:
        return False