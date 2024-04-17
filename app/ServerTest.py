import unittest
import requests
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import os
from Database import USER, PASSWORD, HOST
import subprocess as sp

TEST_DBNAME = "TEST_DB"
Server.DBNAME = TEST_DBNAME

BACKEND = "http://localhost:5000/api"

def run_query(query, dbname=TEST_DBNAME):
    conn = psycopg2.connect(dbname=dbname, user=USER, password=PASSWORD, host=HOST)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
    except Exception as e:
        pass
    cursor.close()
    conn.close()

class ServerTest(unittest.TestCase):
    def setUp(self):
        run_query(f'CREATE DATABASE "{TEST_DBNAME}";', dbname='postgres')

    def tearDown(self):
        run_query(f'DROP DATABASE "{TEST_DBNAME}";', dbname='postgres')


    def test_server_reachability(self):
        response = requests.get(f"{BACKEND}/test")
        self.assertEqual(response.status_code, 200, response.content)

    def test_server_create_user(self):
        data = {"username": "testuser", "password": "testpassword"}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND}/createuser", json=data, headers=headers)
        self.assertEqual(response.status_code, 200, response.content)


if __name__ == "__main__":
    unittest.main()