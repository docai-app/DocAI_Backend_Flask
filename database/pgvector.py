import os
import psycopg2

class PGVectorDB:
    def __init__(self, name):
        self.conn = psycopg2.connect(os.getenv(name))
