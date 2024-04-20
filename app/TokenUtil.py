from datetime import datetime, timezone, timedelta
import jwt

def get_token(username, timeout, secret_key):
    return jwt.encode({'username': username, 'exp': datetime.now(timezone.utc) + timedelta(seconds=timeout)}, secret_key)
    
def is_token_expired(token_data):
    return token_data['exp'] > datetime.now(timezone.utc).timestamp()
