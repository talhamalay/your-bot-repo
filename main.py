import json
import os
import threading
from flask import Flask
from telegram.ext import Application, MessageHandler, filters

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

# --- Bot Config ---
BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"

async def handle_message(update, context):
    text = update.message.text.lower().strip()
    # Clean input (remove spaces, extra dots etc.)
    clean = "".join(ch for ch in text if ch.isalnum())

    response = None
    for key, value in WORDS.items():
        if clean == key.lower().replace(" ", ""):
            response = value
            break

    if response:
        await update.message.reply_text(response)
    else:
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
