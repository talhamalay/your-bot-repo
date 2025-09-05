import json
import os
from flask import Flask
from threading import Thread
from telegram.ext import Updater, MessageHandler, Filters

# Load dictionary
with open("dictionary.json", "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)

# Function to normalize input (lowercase + strip spaces)
def normalize(text: str) -> str:
    return text.strip().lower()

# Telegram message handler
def handle_message(update, context):
    user_text = normalize(update.message.text)

    # Search in dictionary
    if user_text in DICTIONARY:
        reply = DICTIONARY[user_text]
    else:
        reply = "Soory 😅 Not Added In My Dictionary, Skip Question ⁉️"

    update.message.reply_text(reply)

# Flask app (Render free deploy trick)
app = Flask('')

@app.route('/')
def home():
    return "Bot Running ✅"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    # Flask keep alive
    keep_alive()

    # Your Telegram bot token
    TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"

    # Setup bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start bot
    updater.start_polling()
    updater.idle()
