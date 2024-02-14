from flask import request
import datetime

def get_json(request, *args):
    try:
        data = request.get_json()
        return [data.get(arg) for arg in args]
    except Exception as e:
        return None

def get_token(username):
    return jwt.encode({'user_id': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, secret_key)