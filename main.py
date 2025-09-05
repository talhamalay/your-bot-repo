import json
import os
import threading
from flask import Flask
from telegram.ext import Application, MessageHandler, filters
from rapidfuzz import process

# --- Flask for Render keep-alive ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running fine!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- Load Dictionary ---
with open("dictionary.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

# All keys in lower for matching
DICT_KEYS = [k.lower() for k in WORDS.keys()]

# --- Bot Config ---
BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"

async def handle_message(update, context):
    text = update.message.text.lower().strip()

    # Fuzzy match (90% threshold)
    best_match = process.extractOne(text, DICT_KEYS, score_cutoff=80)

    if best_match:
        matched_key = best_match[0]
        response = WORDS.get(matched_key, None)
        if response:
            await update.message.reply_text(response)
            return

    await update.message.reply_text("❌ Word not found in my dictionary.")

def main():
    # Start Flask server in background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
