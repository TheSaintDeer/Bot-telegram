import sqlite3

def starting():

    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users
                   (first_name TEXT, second_name TEXT, age SMALLINT, description TEXT)''')