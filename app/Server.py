import secrets
from datetime import datetime
from random import randint

import Database as db
import encryption
import psycopg2.extras
import queries
from DBReaderWriter import DBReaderWriter
from flask import Flask, jsonify
from flask_cors import CORS
from Log import getDebugLogger
from Queue import Queue
from ServerUtil import get_json
from Session import Session
from TokenUtil import get_token, get_token_data, is_token_expired

secret_key = secrets.token_hex(32)
app = Flask(__name__)
CORS(app)

LOG = getDebugLogger(__name__)
FIVE_MINUTES = 300

# Initialize the DB writer and reader
DB_WRITER = DBReaderWriter(db.DBNAME, db.USER, db.PASSWORD, db.HOST, "w")
DB_READER = DBReaderWriter(db.DBNAME, db.USER, db.PASSWORD, db.HOST, "r")
DICT_READER = DBReaderWriter(db.DBNAME, db.USER, db.PASSWORD, db.HOST, 'r', cursor_factory=psycopg2.extras.DictCursor)

API = "/api"

# Clear the log file before starting
open('../log/app.log', 'w').close()

@app.route(API + '/test', methods=['GET'])
def api_test():
    return "API is working", 200

@app.route(API + '/createuser', methods=['POST'])
def api_create_user():
    with DB_WRITER as cursor:
        username, password = get_json('username', 'password')
        salt, hashed_password = encryption.get_salt_hash(password)
        queries.create_user(cursor, username, hashed_password, salt)
        LOG.info(f"User {username} created")
        return "User created successfully", 200
    return "Error creating user", 400

@app.route(API + '/login', methods=['POST'])
def api_login():
    with DICT_READER as cursor:
        username, password = get_json('username', 'password')
        LOG.info(f"Logging in user {username}")
        # Check if the user exists
        if not queries.valid_username_password(cursor, username, password):
            raise Exception("Invalid username or password")
        token_duration = dict(queries.get_user_options(cursor, username))['token_duration']
        token = get_token(username, token_duration, secret_key)
        LOG.info(f"User {username} logged in")
        return jsonify({'token': token}), 200
    return "Error logging in", 400

# Logging out is handled by the client. Just delete the token from local storage.

@app.route(API + '/getuser', methods=['POST'])
def api_get_user():
    token = get_json('token')[0]
    token_data = get_token_data(token, secret_key)
    if is_token_expired(token_data):
        return "Token expired", 401

    username = token_data['username']
    with DICT_READER as cursor:
        user = dict(queries.get_user_options(cursor, username))
        LOG.info(f"Fetched user {username}")
        return jsonify(user), 200
    return "Error fetching user", 400

@app.route(API + '/setuseroptions', methods=['POST'])
def api_set_user_options():
    token, user_options = get_json('token', 'user_options')
    token_data = get_token_data(token, secret_key)
    if is_token_expired(token_data):
        return "Token expired", 401
    # Make sure the auto logout is not so short that they cannot change it
    user_options['token_duration'] = max(FIVE_MINUTES, int(user_options['token_duration']))
    
    with DB_WRITER as cursor:
        LOG.info(f"{user_options}")
        username = token_data["username"]
        queries.set_user_options(cursor, username, user_options)
        LOG.info(f"Updated user data for {username}")
        return "Updated user options", 200
    return "Error updating user options", 400

@app.route(API + '/getscores', methods=['POST'])
def api_get_scores():
    token, max_rows = get_json('token', 'max_rows')
    token_data = get_token_data(token, secret_key)
    if is_token_expired(token_data):
        return "Token expired", 401
    
    with DB_READER as cursor:
        username = token_data['username']
        scores = queries.get_scores(cursor, username, max_rows)
        LOG.info(f"Fetched scores for user {username}")
        return jsonify({'scores': scores}), 200
    return "Error fetching scores", 400

@app.route(API + '/addscore', methods=['POST'])
def api_add_score():
    token, wpm, accuracy, elapsed_time = get_json('token', 'wpm', 'accuracy', 'elapsed_time')
    token_data = get_token_data(token, secret_key)
    if is_token_expired(token_data):
        return "Token expired", 401
    
    with DB_WRITER as cursor:
        username = token_data['username']
        queries.add_score(cursor, username, wpm, accuracy, elapsed_time)
        LOG.info(f"Score added for user {username}")
        return "Score added successfully", 200
    return "Error adding score to user", 400

@app.route(API + '/savefeedback', methods=['POST'])
def api_save_feedback():
    with open('../feedback/feedback.txt', 'a') as file:
        feedback = get_json("feedback")
        feedback_string = f"[{datetime.now()}] - {feedback}"
        file.write(feedback_string + '\n')
        LOG.info(f"Feedback received: {feedback}")
        return "Feedback saved successfully", 200
    return "Error saving feedback", 400

@app.route(API + '/getparagraph', methods=['GET'])
def api_get_paragraph():
    with open('../paragraphs.txt', 'r') as file:
        number_of_paragraphs = int(file.readline())
        chosen_paragraph_index = randint(0, number_of_paragraphs - 1)
        for i, line in enumerate(file):
            if i == chosen_paragraph_index: 
                return line, 200
    return "Could not fetch new paragraph", 400

@app.route(API + '/getleaderboard', methods=['POST'])
def api_get_leaderboard():
    lb_type, max_rows = get_json('type', 'max_rows')
    with DB_READER as cursor:
        return queries.get_leaderboard(cursor, lb_type, max_rows), 200
    return "Failed to get leaderboard", 400

# Seems like a lot of potential memory usage depending on how many 
# people are in the queue, and how often they leave and join
player_queue = Queue()
session_ids = {}
sessions = {}

@app.route(API + '/joinqueue', methods=['POST'])
def api_join_queue():
    token = get_json('token')[0]
    token_data = get_token_data(token, secret_key)
    username = token_data['username']

    if is_token_expired(token_data):
        return "Token expired", 401
    if player_queue.put(username):
        return "Player added to queue", 200
    return "Player already in queue", 400

@app.route(API + '/leavequeue', methods=['POST'])
def api_leave_queue():
    token = get_json('token')[0]
    token_data = get_token_data(token, secret_key)
    username = token_data['username']
    if is_token_expired(token_data):
        return "Token expired", 401
    
    if player_queue.mark_for_removal(username):
        return "Player removed from queue", 200
    return "Player not in queue", 400

@app.route(API + '/getmatch', methods=['POST'])
def api_get_match():
    token = get_json('token')[0]
    token_data = get_token_data(token, secret_key)
    username = token_data['username']

    if is_token_expired(token_data):
        return "Token expired", 401
    
    # If a session was already found for this player
    if username in session_ids:
        return jsonify({'session_id': session_ids.pop(username)}), 200
    
    if not player_queue.contains(username):
        return "Player isn't in queue", 400
    if player_queue.qsize() < 2:
        return "Not enough players in queue", 202
    
    player1 = player_queue.get()
    player2 = player_queue.get()

    session_id = secrets.token_hex(16)
    sessions[session_id] = Session()
    if player1 == username:
        session_ids[player2] = session_id
        return jsonify({'match_id': session_id}), 200
    elif player2 == username:
        session_ids[player1] = session_id
        return jsonify({'match_id': session_id}), 200
    else:
        # Even if we aren't in the queue, we can do some computing for the other players
        # This way, we are not reliant on the other players to advance the queue
        session_ids[player1] = session_id
        session_ids[player2] = session_id
        return "Waiting for match", 202

@app.route(API + '/sendmatchdata', methods=['POST'])
def api_send_match_data():
    token, match_id, key_events = get_json('token', 'match_id', 'key_events')
    if key_events == None or len(key_events) == 0:
        return "No key events received", 400
    token_data = get_token_data(token, secret_key)
    username = token_data['username']
    session = sessions[match_id]
    session.write_buffer(username, key_events)
    return "Match data recieved", 200

@app.route(API + '/getmatchdata', methods=['POST'])
def api_get_match_data():
    token, match_id = get_json('token', 'match_id')
    token_data = get_token_data(token, secret_key)
    username = token_data['username']
    session = sessions[match_id]
    match_data = session.read_buffer(username)
    return jsonify({'match_data': match_data}), 200

    