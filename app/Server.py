from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import queries
import encryption
from encryption import get_json, is_token_expired
import secrets
import jwt
import Database as db
from DBReaderWriter import DBReaderWriter
from psycopg2 import sql
import psycopg2.extras
from Log import getDebugLogger
from datetime import datetime
from random import randint
from queue import Queue
from Session import Session
import json

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
DASHBOARD = "/dashboard"

# Clear the log file before starting
open('../log/app.log', 'w').close()

@app.route(API + '/test', methods=['GET'])
def api_test():
    return "API is working", 200

@app.route(API + '/createuser', methods=['POST'])
def api_create_user():
    with DB_WRITER as cursor:
        username, password = get_json(request, 'username', 'password')
        salt, hashed_password = encryption.get_salt_hash(password)
        queries.create_user(cursor, username, hashed_password, salt)
        LOG.info(f"User {username} created")
        return "User created successfully", 200
    return "Error creating user", 400

@app.route(API + '/login', methods=['POST'])
def api_login():
    with DICT_READER as cursor:
        username, password = get_json(request, 'username', 'password')
        LOG.info(f"Logging in user {username}")
        # Check if the user exists
        if not queries.valid_username_password(cursor, username, password):
            raise Exception("Invalid username or password")
        token_duration = dict(queries.get_user_options(cursor, username))['token_duration']
        token = encryption.get_token(username, token_duration, secret_key)
        LOG.info(f"User {username} logged in")
        return jsonify({'token': token}), 200
    return "Error logging in", 400

# Logging out is handled by the client. Just delete the token from local storage.

@app.route(API + '/getuser', methods=['POST'])
def api_get_user():
    token = get_json(request, 'token')[0]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    if not is_token_expired(token_data):
        return "Token expired", 401

    username = token_data['username']
    with DICT_READER as cursor:
        user = dict(queries.get_user_options(cursor, username))
        LOG.info(f"Fetched user {username}")
        return jsonify(user), 200
    return "Error fetching user", 400

@app.route(API + '/setuseroptions', methods=['POST'])
def api_set_user_options():
    token, user_options = get_json(request, 'token', 'user_options')
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    if not is_token_expired(token_data):
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
    token, max_rows = get_json(request, 'token', 'max_rows')
    token_data = jwt.decode(token.encode('utf-8'), secret_key, algorithms=["HS256"])
    if not is_token_expired(token_data):
        return "Token expired", 401
    
    with DB_READER as cursor:
        username = token_data['username']
        scores = queries.get_scores(cursor, username, max_rows)
        LOG.info(f"Fetched scores for user {username}")
        return jsonify({'scores': scores}), 200
    return "Error fetching scores", 400

@app.route(API + '/addscore', methods=['POST'])
def api_add_score():
    token, wpm, accuracy, elapsed_time = get_json(request, 'token', 'wpm', 'accuracy', 'elapsed_time')
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    if not is_token_expired(token_data):
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
        feedback = request.json['feedback']
        feedback_string = f"[{datetime.now()}] - {feedback}"
        file.write(feedback_string + '\n')
        LOG.info(f"Feedback received: {feedback}")
        return "Feedback saved successfully", 200
    return "Error saving feedback", 400

@app.route(API + '/getparagraph', methods=['GET'])
def api_get_paragraph():
    with open('../paragraphs.txt', 'r') as file:
        n = int(file.readline())
        fn = randint(0, n - 1)
        # This is O(n), but n stays constant so it is kinda O(1)
        # Still if there are too many paragraphs it could get slow.
        # For the number of paragraphs im using it is quick enough
        for i, line in enumerate(file):
            if i == fn: 
                return line, 200
    return "Could not fetch new paragraph", 400

@app.route(API + '/getleaderboard', methods=['POST'])
def api_get_leaderboard():
    lb_type, max_rows = get_json(request, 'type', 'max_rows')
    with DB_READER as cursor:
        return queries.get_leaderboard(cursor, lb_type, max_rows), 200
    return "Failed to get leaderboard", 400
