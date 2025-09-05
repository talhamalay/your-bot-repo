import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask app for Render keep-alive
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running fine on Render 🚀"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# Telegram bot
TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"

app = Application.builder().token(TOKEN).build()

# Example handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is live ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

if __name__ == "__main__":
    # Run Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # Run Telegram bot (non-blocking)
    app.run_polling(drop_pending_updates=True, close_loop=False)
