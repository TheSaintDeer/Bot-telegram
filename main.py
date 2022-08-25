import telebot
from telebot import types
import sqlite3
from games import TTT

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
    CREATE TABLE IF NOT EXISTS game_ttt(
        host VARCHAR(20) PRIMARY KEY NOT NULL,
        player VARCHAR(20) NOT NULL,
        turn INT NOT NULL
    )
    """

    cursor.executescript(query)

API_TOKEN = '5491063411:AAHuG5JGbBJqBQOpxiskOiPy2FEdsnCPxOQ'
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

def start_game(call, tag_game):
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

        elif int(chat) == int(player[0]):
            bot.send_message(chat, "You are already looking for a game.")

        else:
            bot.send_message(player[0], f"Game found. Your opponent is {call.from_user.username}")
            cursor.execute("SELECT id_user FROM users WHERE id_chat=?", [player[0],])
            bot.send_message(chat, f"Game found. Your opponent is {cursor.fetchone()[0]}")

            cursor.execute("DELETE FROM queue WHERE id_chat=? AND game=?", (player[0], tag_game))
            db.commit()
            
    except sqlite3.Error as e:
        print(f"Error: {e}!")
    
    finally:
        cursor.close()
        db.close()

@bot.callback_query_handler(func = lambda call: True)
def games(call):

    if call.data == "Tic_Tac_Toe":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_game(call, "TTT")
        

bot.infinity_polling()