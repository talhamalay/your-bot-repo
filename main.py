import os
import json
import telebot
from flask import Flask, request

# ---------------------------
# Load dictionary.json
# ---------------------------
with open("dictionary.json", "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)

# ---------------------------
# Telegram Bot Token
# ---------------------------
TOKEN = os.getenv("BOT_TOKEN", "8497771770:AAE_AeqqjYuq1KL-pAXdgoXp0HVfiXcJ5rM")
bot = telebot.TeleBot(TOKEN)

# ---------------------------
# Flask App (Render ke liye)
# ---------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

# ---------------------------
# Telegram Message Handler
# ---------------------------
@bot.message_handler(func=lambda message: True)
def reply_message(message):
    user_text = message.text.strip().lower()

    # Agar user ka text dictionary me hai to wahi reply
    if user_text in DICTIONARY:
        bot.reply_to(message, DICTIONARY[user_text])
    else:
        # Agar nahi mila to fixed reply
        bot.reply_to(message, "❌ Sorry, Not Added in My Dictionary. Skip Question ⁉️")

# ---------------------------
# Start Bot + Flask Server
# ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Run bot in polling (Render background service ka charge leta hai, isliye polling Flask ke sath chalate hain)
    import threading
    threading.Thread(target=lambda: bot.polling(none_stop=True, interval=0)).start()
    app.run(host="0.0.0.0", port=port)
