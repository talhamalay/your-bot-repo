import json
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from rapidfuzz import process

# --- Flask for Render keep-alive ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running fine on Render 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# --- Load Dictionary ---
with open("dictionary.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

# All keys lowercase for matching
DICT_KEYS = [k.lower() for k in WORDS.keys()]

# --- Bot Config ---
BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"
bot_app = Application.builder().token(BOT_TOKEN).build()

# --- Handlers ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    # Fuzzy match (80% threshold)
    best_match = process.extractOne(text, DICT_KEYS, score_cutoff=80)

    if best_match:
        matched_key = best_match[0]
        response = WORDS.get(matched_key, None)
        if response:
            await update.message.reply_text(response)
            return

    await update.message.reply_text("❌ Word not found in my dictionary.")

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Main ---
if __name__ == "__main__":
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # Run Telegram bot
    bot_app.run_polling(drop_pending_updates=True, close_loop=False)
