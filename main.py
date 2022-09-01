import telebot
from telebot import types
import sqlite3
import re

with sqlite3.connect("database.db") as db:
    cursor = db.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS users(
        id_chat VARCHAR(20) PRIMARY KEY NOT NULL,
        id_user VARCHAR(30) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS queue(
        id_chat VARCHAR(20) NOT NULL REFERENCES users,
        game VARCHAR(3) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS ttt(
        chat_host VARCHAR(20) PRIMARY KEY NOT NULL,
        chat_player VARCHAR(20) NOT NULL,
        turn VARCHAR(1) NOT NULL,
        play_table VARCHAR(9) NOT NULL,
        message_host VARCHAR(20),
        message_player VARCHAR(20)
    );
    """

    cursor.executescript(query)

API_TOKEN = 'API_of_your_bot'
bot = telebot.TeleBot(API_TOKEN)

def sign_up(message):
    user = message.from_user.username
    chat = message.chat.id

    try: 
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        cursor.execute("SELECT id_chat FROM users WHERE id_chat=?", [chat])
        if cursor.fetchone() is None:
            values = [chat, user]

            cursor.execute("INSERT INTO users(id_chat, id_user) VALUES(?, ?)", values)
            db.commit()
            
    except sqlite3.Error as e:
        print(f"Error: {e}!")
    
    finally:
        cursor.close()
        db.close()

@bot.message_handler(commands=['start'])
def start(message):
    sign_up(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='❌Tic Tac Toe⭕', callback_data='Tic_Tac_Toe'))

    bot.send_message(message.chat.id, "Hi there, I am GameBot.\nI am here to play with other people.")
    bot.send_message(message.chat.id, "You can chose game.", reply_markup=markup)

def find_game(call, tag_game):
    chat = call.message.chat.id

    try: 
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        cursor.execute("SELECT * FROM queue WHERE game=?", [tag_game])
        player = cursor.fetchone()
        if player is None:
            values = [chat, tag_game]

            cursor.execute("INSERT INTO queue(id_chat, game) VALUES(?, ?)", values)
            db.commit()
            cursor.close()
            db.close()

        elif int(chat) == int(player[0]):
            bot.send_message(chat, "You are already looking for a game.")

        else:
            bot.send_message(player[0], f"Game found. Your opponent is {call.from_user.username}")
            cursor.execute("SELECT id_user FROM users WHERE id_chat=?", [player[0],])
            bot.send_message(chat, f"Game found. Your opponent is {cursor.fetchone()[0]}")

            cursor.execute("DELETE FROM queue WHERE id_chat=? AND game=?", (player[0], tag_game))
            db.commit()
            cursor.close()
            db.close()

            game_TTT(chat, player[0])
            
    except sqlite3.Error as e:
        print(f"Error: {e}!")

def game_TTT(host, player):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3

    for i in range(3):
        btn = []
        for j in range(3):
            btn.append(types.InlineKeyboardButton(text='⬜', callback_data='TTT'+str(i)+str(j)))

        markup.add(btn[0], btn[1], btn[2])

    msg_host = bot.send_message(host, "Rules:", reply_markup=markup)
    msg_player = bot.send_message(player, "Rules:", reply_markup=markup)

    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        values = [str(msg_host.chat.id), str(msg_player.chat.id), "0", "000000000", str(msg_host.message_id), str(msg_player.message_id)]
        cursor.execute("INSERT INTO ttt(chat_host, chat_player, turn, play_table, message_host, message_player) VALUES(?, ?, ?, ?, ?, ?)", values)
        db.commit()

    except sqlite3.Error as e:
        print(f"Error: {e}!")

    finally:
        cursor.close()
        db.close()

def check_user(call, cell):
    chat_user_id = call.message.chat.id

    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        cursor.execute("SELECT * FROM ttt WHERE turn='0' AND chat_host=? OR turn='1' AND chat_player=?", [chat_user_id, chat_user_id])
        row = cursor.fetchone() 
        new_row = []
        index = int(cell[0])*3 + int(cell[1])

        if row:
            if row[3][index] == '0':
                if row[2] == "0":

                    new_row.append('1')
                    string = row[3][:index] + '1' + row[3][index+1:]
                    new_row.append(string)
                else:

                    new_row.append('0')
                    string = row[3][:index] + '2' + row[3][index+1:]
                    new_row.append(string)

                new_row.append(row[0])
                cursor.execute("UPDATE ttt SET turn=?, play_table=? WHERE chat_host=?", new_row)
                db.commit()

                update_table(row[0], row[1], row[2], new_row[1], call, row[4], row[5])

            else:
                bot.send_message(chat_user_id, "Cell is busy! Choose other!")
            
        else:
            bot.send_message(chat_user_id, "Don't your turn! Wait!")

    except sqlite3.Error as e:
        print(f"Error: {e}!")

    finally:
        cursor.close()
        db.close()

def update_table(host, player, turn, cells, call, m_host, m_player):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3

    for i in range(3):
        btn = []
        sign = ""
        for j in range(3):
            if cells[j + i*3] == "0":
                sign = "⬜"
            elif cells[j + i*3] == "1":
                sign = "❌"
            else:
                sign = "⭕"

            btn.append(types.InlineKeyboardButton(text=sign, callback_data='TTT'+str(i)+str(j)))

        markup.add(btn[0], btn[1], btn[2])

    if turn == "0":
        bot.edit_message_text(chat_id=host, message_id=call.message.message_id, text="Rules:", reply_markup=markup)
        bot.edit_message_text(chat_id=player, message_id=m_player, text="Rules:", reply_markup=markup)

    else:
        bot.edit_message_text(chat_id=player, message_id=call.message.message_id, text="Rules:", reply_markup=markup)
        bot.edit_message_text(chat_id=host, message_id=m_host, text="Rules:", reply_markup=markup)

    check_win(host, player, m_host, m_player, cells)

def check_win(host, player, m_host, m_player, cells):
    win = 2
    winning_comb = [cells[0]+cells[4]+cells[8],
                    cells[6]+cells[4]+cells[2],
                    cells[0]+cells[1]+cells[2],
                    cells[3]+cells[4]+cells[5],
                    cells[6]+cells[7]+cells[8],
                    cells[0]+cells[3]+cells[6],
                    cells[1]+cells[4]+cells[7],
                    cells[2]+cells[5]+cells[8]]
    
    if '111' in winning_comb:
        win = 0
    elif '222' in winning_comb:
        win = 1

    if win < 2:

        bot.delete_message(host, m_host)
        bot.delete_message(player, m_player)

        try:
            db = sqlite3.connect("database.db")
            cursor = db.cursor()

            cursor.execute("DELETE FROM ttt WHERE chat_host=?", [host,])
            db.commit()

            if win == 0:
               cursor.execute("SELECT id_user FROM users WHERE id_chat=?", (host,))
            else:
               cursor.execute("SELECT id_user FROM users WHERE id_chat=?", (player,)) 

            winner = cursor.fetchone()[0]
            bot.send_message(host, f"Winner: {winner}")
            bot.send_message(player, f"Winner: {winner}")

        except sqlite3.Error as e:
            print(f"Error: {e}!")

        finally:
            cursor.close()
            db.close()

    elif not '0' in list(cells):

        bot.delete_message(host, m_host)
        bot.delete_message(player, m_player)

        try:
            db = sqlite3.connect("database.db")
            cursor = db.cursor()

            cursor.execute("DELETE FROM ttt WHERE chat_host=?", [host,])
            db.commit()

            bot.send_message(host, "Draw")
            bot.send_message(player, "Draw")

        except sqlite3.Error as e:
            print(f"Error: {e}!")

        finally:
            cursor.close()
            db.close()

@bot.callback_query_handler(func = lambda call: True)
def games(call):

    if call.data == "Tic_Tac_Toe":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        find_game(call, "TTT")
    if re.findall('^T{3}[0-2]{2}$', call.data):
        cell = re.sub('^T{3}', '', call.data)
        check_user(call, cell)

bot.infinity_polling()