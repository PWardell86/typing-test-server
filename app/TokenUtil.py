import datetime
import jwt

def get_token(username, timeout, secret_key):
    return jwt.encode({'username': username, 'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=timeout)}, secret_key)

def get_token_data(token, secret_key):
    return jwt.decode(token, secret_key, algorithms=["HS256"])

def is_token_expired(token_data):
    return token_data['exp'] > datetime.datetime.now(datetime.UTC).timestamp()

