import telebot
import json
from flask import Flask

# Apna bot token (NEW)
TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"
bot = telebot.TeleBot(TOKEN)

# Dictionary load karna
with open("dictionary.json", "r", encoding="utf-8") as f:
    responses = json.load(f)

app = Flask(__name__)

@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.lower()
    if text in responses:
        bot.reply_to(message, responses[text])
    else:
        bot.reply_to(message, "Sorry! Not added in my dictionary. Skip question ⁉️")

@app.route('/')
def index():
    return "Bot is running!"

import threading
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
