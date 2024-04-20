from flask import request

def get_json(*args):
    try:
        data = request.get_json()
        return [data.get(arg) for arg in args]
    except Exception as e:
        return None
    
