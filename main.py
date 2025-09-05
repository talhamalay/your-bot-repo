import os
import threading
import json
from flask import Flask
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram import Update
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

# --- Bot Config ---
BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0"
ADMIN_ID = "7053615484"

# --- Bad Words List ---
BAD_WORDS = [
    "bc", "mc", "taxi", "taxi orat", "bhenchod", "madarchod", "chadarmod",
    "bhen ka loda", "bhen ke lodi", "ghasti ka bacha", "ghasti orat",
    "uc", "ac", "lol", "lool", "bgyrat", "pagal", 
    "teri maa ka phuda", "teri maa ke phudi", 
    "tery bhen ko lund", "teri bhen ko lumd",
    "jhail", "jahil", "jhil"
]

# --- Helper: User Data Storage ---
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = f"@{user.username}" if user.username else user.first_name
    uid = str(user.id)

    users = load_users()
    if uid not in users:
        users[uid] = {
            "name": name,
            "age": "❌ Not set",
            "gender": "❌ Not set",
            "city": "❌ Not set",
            "preferred_city": "❌ Not set",
            "hobbies": "❌ Not set",
            "whatsapp": "❌ Not given",
            "telegram": name,
            "photo": None,
            "premium": False
        }
        save_users(users)

    await update.message.reply_text(
        f"👋 Welcome {name}!\n\n"
        "This is your personal bot 🤖✨\n"
        "I’m here to make your journey easier & more fun 🚀\n\n"
        "Type /help to see what I can do for you!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Need some help?\n\n"
        "Here’s what I can do for you:\n\n"
        "/start - Launch the bot\n"
        "/help - Get help & guidance\n"
        "/about - Know more about me\n"
        "/settings - Customize your experience\n"
        "/contact - Connect with the admin 👤\n"
        "/userprofile <id> - (Admin only) View user profile"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = f"@{user.username}" if user.username else user.first_name
    await update.message.reply_text(
        f"ℹ️ About this bot, {name}:\n\n"
        "I’m created to assist you with quick responses, info & guidance 🚀\n"
        "Always here to make your day better 🌟"
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = f"@{user.username}" if user.username else user.first_name
    await update.message.reply_text(
        f"⚙️ Settings Panel for you, {name}:\n\n"
        "Here you can manage your preferences, customize how I respond,\n"
        "and adjust things just the way you like 💡"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = f"@{user.username}" if user.username else user.first_name
    await update.message.reply_text(
        f"📩 Hey {name}, here are the admin contact details:\n\n"
        "👤 Name: Talha Mehmood\n"
        "📞 Phone: +92 305 2722877\n"
        "✉️ Email: lartkapagal@gmail.com\n\n"
        "Feel free to reach out anytime 🤝"
    )

# --- Admin Only: User Profile ---
async def userprofile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != ADMIN_ID:
        await update.message.reply_text("⛔ Only admin can use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /userprofile <user_id>")
        return

    uid = context.args[0]
    users = load_users()

    if uid in users:
        u = users[uid]
        text = (
            f"📂 User Profile (ID: {uid}):\n\n"
            f"Name: {u['name']}\n"
            f"Age: {u['age']}\n"
            f"Gender: {u['gender']}\n"
            f"City: {u['city']}\n"
            f"Preferred City: {u.get('preferred_city', '❌ Not set')}\n"
            f"Hobbies: {u['hobbies']}\n"
            f"WhatsApp: {u.get('whatsapp', '❌ Not given')}\n"
            f"Telegram: {u.get('telegram', '❌ Not given')}\n"
            f"Premium: {'✅ Yes' if u.get('premium') else '❌ No'}"
        )
        await update.message.reply_text(text)

        if u.get("photo"):
            try:
                await update.message.reply_photo(photo=open(u["photo"], "rb"))
            except:
                await update.message.reply_text("⚠️ Could not load photo.")
    else:
        await update.message.reply_text("❌ User not found.")

# --- Dictionary & Bad Word Filter ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    # 🔥 Bad Word Check
    for bad in BAD_WORDS:
        if bad in text:
            try:
                await update.message.delete()
            except:
                pass
            user = update.message.from_user
            name = f"@{user.username}" if user.username else user.first_name
            await update.message.chat.send_message(
                f"⚠️ Please avoid using bad words, {name}!"
            )
            return

    # Dictionary Search
    best_match = process.extractOne(text, DICT_KEYS, score_cutoff=80)
    if best_match:
        matched_key = best_match[0]
        response = WORDS.get(matched_key, None)
        if response:
            await update.message.reply_text(response)
            return

    await update.message.reply_text("❌ Word not found in my dictionary.")

# --- Main Runner ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()

    bot_app = Application.builder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("about", about))
    bot_app.add_handler(CommandHandler("settings", settings))
    bot_app.add_handler(CommandHandler("contact", contact))
    bot_app.add_handler(CommandHandler("userprofile", userprofile))

    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    bot_app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
