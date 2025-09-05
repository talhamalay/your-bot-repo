import imghdr  # force import so telegram library works
from flask import Flask
from telegram.ext import Updater, MessageHandler, Filters
import difflib
import json

# ---------------- Flask Server ----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running successfully!"

# ---------------- Load Dictionary ----------------
with open("dictionary.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)

# ---------------- Telegram Bot Setup ----------------
TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"  # <-- Aapka Bot Token
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# User ke liye suggestions store karne ka dict
user_suggestions = {}

# ---------------- Matching Function ----------------
def find_reply(text, user_id):
    text = text.lower().strip()
    keys = list(dictionary.keys())

    # Agar user "yes" bole aur uske liye suggestion store hai
    if text == "yes" and user_id in user_suggestions:
        suggested_key = user_suggestions[user_id]
        del user_suggestions[user_id]
        return dictionary[suggested_key]

    # Normal fuzzy match (cutoff=0.6)
    matches = difflib.get_close_matches(text, keys, n=1, cutoff=0.6)
    if matches:
        return dictionary[matches[0]]

    # Suggestion dena (cutoff=0.3 for loose matching)
    suggestion = difflib.get_close_matches(text, keys, n=1, cutoff=0.3)
    if suggestion:
        user_suggestions[user_id] = suggestion[0]
        return f"❓ Did you mean: '{suggestion[0]}' ? Reply with 'Yes' to confirm."
    
    # Agar kuch bhi match na mile
    return "❌ Sorry, I don’t understand. Try another word!"

# ---------------- Handler ----------------
def handle_message(update, context):
    user_text = update.message.text
    user_id = update.message.from_user.id
    reply = find_reply(user_text, user_id)
    update.message.reply_text(reply)

# ---------------- Dispatcher ----------------
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# ---------------- Start Bot ----------------
if __name__ == "__main__":
    updater.start_polling()
    app.run(host="0.0.0.0", port=5000)
