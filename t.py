import sqlite3

con = sqlite3.connect('users.db', check_same_thread=False)
cur = con.cursor()
cur.execute('''DROP TABLE tic_tac_toe''')