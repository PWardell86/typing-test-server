import psycopg2
import logging
from Log import getDebugLogger

LOG = getDebugLogger(__name__)

class DBWriter:
    def __init__(self, dbname, user, password, host, mode):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.conn = None
        self.cursor = None
        self.mode = mode

    def __enter__(self):
        self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            LOG.error(exc_value)
            self.conn.rollback()
        elif not "w" in self.mode:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
        return True
