import telebot
from telebot import types
import sqlite3

with sqlite3.connect("database.db") as db:
    cursor = db.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS users(
        id_chat VARCHAR(20) PRIMARY KEY NOT NULL,
        id_user VARCHAR(30) NOT NULL
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

        cursor.execute("SELECT id_user FROM users WHERE id_user=?", [chat])
        if cursor.fetchone() is None:
            values = [chat, user]

            cursor.execute("INSERT INTO users(id_chat, id_user) VALUES(?, ?)", values)
            db.commit()
            
    except sqlite3.Error as e:
        print("Error!")
    
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

@bot.callback_query_handler(func = lambda call: True)
def games(call):

    if call.data == "Tic_Tac_Toe":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "I'm looking for user for you.")
    

bot.infinity_polling()