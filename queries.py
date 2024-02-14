import encryption
import datetime

def create_user(cursor, username, password, salt):
    query = f"INSERT INTO USERS (username, password, salt, display_name) VALUES ('{username}', '{password}', '{salt}', '{username}')"
    cursor.execute(query)

def valid_username_password(cursor, username, password):
    query = f"SELECT password, salt FROM USERS WHERE username = '{username}'"
    cursor.execute(query)
    if cursor.rowcount != 1:
        return False
    expeceted_hash, salt = cursor.fetchone()
    return encryption.valid_password(password, salt, expeceted_hash)

def get_user(cursor, username):
    query = f"SELECT * FROM USERS WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

def get_scores(cursor, username, limit):
    query = f"SELECT date, accuracy, wpm, elapsed_time FROM USER_SCORE WHERE username = '{username}' ORDER BY date DESC LIMIT {limit}"
    cursor.execute(query)
    return cursor.fetchall()

def add_score(cursor, username, wpm, accuracy, elapsed_time):
    query = f"INSERT INTO USER_SCORE (username, wpm, accuracy, elapsed_time, date) VALUES ('{username}', {wpm}, {accuracy}, {elapsed_time}, '{datetime.datetime.now()}')"
    cursor.execute(query)
    return cursor.rowcount == 1
