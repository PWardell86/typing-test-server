from flask import request
import re

BAD_CHAR = ""

def get_json(*args):
    try:
        data = request.get_json()
        return [data.get(arg) for arg in args]
    except Exception as e:
        return None

def contains_bad_char(check):
    for ch in check:
        ord_ch = ord(ch)
        if not(48 <= ord_ch <= 57 or 65 <= ord_ch <= 90 or 97 <= ord_ch <= 122 or ord_ch in (45, 46, 95)):
            return False
            
