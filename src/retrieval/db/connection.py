import sqlite3

def get_connection():
    return sqlite3.connect("file:data/ridewise.db?mode=ro", uri=True)
