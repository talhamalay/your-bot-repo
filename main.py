import os
import threading
import json
from flask import Flask
from telegram.ext import Application, MessageHandler, filters
from rapidfuzz import process

# --- Flask App for Render ---
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Bot is running fine on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# --- Load Dictionary ---
with open("dictionary.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

DICT_KEYS = [k.lower() for k in WORDS.keys()]

BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"

async def handle_message(update, context):
    text = update.message.text.lower().strip()
    best_match = process.extractOne(text, DICT_KEYS, score_cutoff=80)

    if best_match:
        matched_key = best_match[0]
        response = WORDS.get(matched_key, None)
        if response:
            await update.message.reply_text(response)
            return

    await update.message.reply_text("❌ Word not found in my dictionary.")

def main():
    # Start Flask server (background thread)
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram bot
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
