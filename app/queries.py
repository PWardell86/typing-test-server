import encryption
import datetime

def create_user(cursor, username, password, salt):
    query = f"""
    INSERT INTO USERS (username, password, salt) VALUES ('{username}', '{password}', '{salt}');
    INSERT INTO USER_OPTIONS (username, display_name) VALUES ('{username}', '{username}');
    """
    cursor.execute(query)

def get_user_options(cursor, username):
    query = f"SELECT * FROM USER_OPTIONS WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

def set_user_options(cursor, username, options):
    query = f"""
    UPDATE USER_OPTIONS 
    SET 
        token_duration = {options['token_duration']}, 
        default_theme = '{options['default_theme']}', 
        display_name = '{options['display_name']}'
    WHERE username = '{username}'
    """
    cursor.execute(query)

def valid_username_password(cursor, username, password):
    query = f"SELECT password, salt FROM USERS WHERE username = '{username}'"
    cursor.execute(query)
    if cursor.rowcount != 1:
        return False
    expeceted_hash, salt = cursor.fetchone()
    return encryption.valid_password(password, salt, expeceted_hash)

def get_user_options(cursor, username):
    query = f"SELECT * FROM USER_OPTIONS WHERE username = '{username}'"
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

def get_leaderboard(cursor, lb_type, max_rows):
    if lb_type == "wpm":
        query = f"""
            SELECT uo.username, uo.display_name, score.wpm 
            FROM user_options uo, user_score score 
            WHERE score.username = uo.username
                AND score.wpm >= ALL (
                    SELECT score2.wpm FROM user_score score2 WHERE score2.username = score.username
                )
            ORDER BY score.wpm DESC
            LIMIT {max_rows}
        """
    cursor.execute(query)
    return cursor.fetchall()
