from flask import Flask, request, jsonify
from flask_cors import CORS
import queries
import encryption
from encryption import get_json
import secrets
import jwt
import Database as db
from DBWriter import DBWriter
from psycopg2 import sql
from Log import getDebugLogger


secret_key = secrets.token_hex(32)
app = Flask(__name__)
CORS(app)

LOG = getDebugLogger(__name__)

DB_WRITER = DBWriter(db.DBNAME, db.USER, db.PASSWORD, db.HOST, "w")
DB_READER = DBWriter(db.DBNAME, db.USER, db.PASSWORD, db.HOST, "r")


@app.route('/api/test', methods=['GET'])
def api_test():
    return "API is working", 200

@app.route('/api/createuser', methods=['POST'])
def api_create_user():
    with DB_WRITER as cursor:
        username, password = get_json(request, 'username', 'password')
        salt, hashed_password = encryption.get_salt_hash(password)
        LOG.info(f"Creating user {username} with password {hashed_password} and salt {salt}")
        queries.create_user(cursor, username, hashed_password, salt)
        return "User created successfully", 200
    return "Error creating user", 400

@app.route('/api/login', methods=['POST'])
def api_login():
    with DB_READER as cursor:
        username, password = get_json(request, 'username', 'password')
        LOG.info(f"Logging in user {username}")
        # Check if the user exists
        if not queries.valid_username_password(cursor, username, password):
            raise Exception("Invalid username or password")
        token = encryption.get_token(username, secret_key)
        return jsonify({'token': token}), 200
    return "Error logging in", 400

@app.route('/api/getuser', methods=['POST'])
def api_get_user():
    with DB_READER as cursor:
        token = get_json(request, 'token')[0]
        dict_data = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = dict_data['username']
        user = queries.get_user(cursor, username)
        return jsonify({'user': user}), 200
    return "Error fetching user", 400

@app.route('/api/getscores', methods=['POST'])
def api_get_scores():
    with DB_READER as cursor:
        token, max_rows = get_json(request, 'token', 'max_rows')
        dict_data = jwt.decode(token.encode('utf-8'), secret_key, algorithms=["HS256"])
        username = dict_data['username']
        scores = queries.get_scores(cursor, username, max_rows)
        return jsonify({'scores': scores}), 200
    return "Error fetching scores", 400

@app.route('/api/addscore', methods=['POST'])
def api_add_score():
    with DB_WRITER as cursor:
        token, wpm, accuracy, elapsed_time = get_json(request, 'token', 'wpm', 'accuracy', 'elapsed_time')
        dict_data = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = dict_data['username']
        queries.add_score(cursor, username, wpm, accuracy, elapsed_time)
        return "Score added successfully", 200
    return "Error adding score to user", 400

app.run(host='0.0.0.0', port=5000)
