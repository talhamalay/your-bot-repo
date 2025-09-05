import telebot
import json
import re
import os

# === Bot Token ===
BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"
bot = telebot.TeleBot(BOT_TOKEN)

# === Load Dictionary ===
if os.path.exists("dictionary.json"):
    with open("dictionary.json", "r", encoding="utf-8") as f:
        responses = json.load(f)
else:
    responses = {}

# === Text Cleaner (normalization) ===
def clean_text(text):
    text = text.lower().strip()                  # lowercase + trim
    text = re.sub(r'[^\w\s]', '', text)          # remove punctuation
    return text

# === Bot Message Handler ===
@bot.message_handler(func=lambda message: True)
def reply(message):
    text = clean_text(message.text)

    if text in responses:
        bot.reply_to(message, responses[text])
    else:
        bot.reply_to(message, "Sorry! Not added in my dictionary. Skip question ⁉️")

# === Run Bot ===
print("🤖 Bot is running...")
bot.infinity_polling()
