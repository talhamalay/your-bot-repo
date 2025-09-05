import os
import threading
import json
import random
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)

# --- Flask App for Render ---
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Bot is running fine on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# --- Bot Token & Admin ---
BOT_TOKEN = "8497771770:AAFlUXMYc6AjSWWyj31TttyvcIww9wFmmCg"
ADMIN_ID = 7053615484     # Only admin can unlock users
ADMIN_USERNAME = "Astryx_7"

# --- File for storing users ---
USERS_FILE = "users.json"

# --- Fixed City Options ---
CITY_OPTIONS = ["Multan", "Lahore", "Bahawalpur", "Murree", "Islamabad"]

# --- Demo Girls Data (promo free numbers) ---
PROMO_GIRLS = [
    {"id": 2001, "name": "Areeba", "city": "Lahore", "gender": "Female",
     "choice_city": "Multan", "photo": "https://i.ibb.co/6nV3Ww6/girl2.jpg", "contact": "+92 300 9812345"},
    {"id": 2002, "name": "Nimra", "city": "Multan", "gender": "Female",
     "choice_city": "Lahore", "photo": "https://i.ibb.co/fDL4Pjv/girl4.jpg", "contact": "+92 301 7723456"},
    {"id": 2003, "name": "Sana", "city": "Bahawalpur", "gender": "Female",
     "choice_city": "Islamabad", "photo": "https://i.ibb.co/vYfVsk7/girl3.jpg", "contact": "+92 302 6634123"},
    {"id": 2004, "name": "Mehak", "city": "Islamabad", "gender": "Female",
     "choice_city": "Murree", "photo": "https://i.ibb.co/n6JRfgV/girl5.jpg", "contact": "+92 303 1122345"},
    {"id": 2005, "name": "Zoya", "city": "Murree", "gender": "Female",
     "choice_city": "Lahore", "photo": "https://i.ibb.co/0jMMvB9/girl1.jpg", "contact": "+92 304 8876543"},
]

# --- Ensure file exists as list ---
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(PROMO_GIRLS, f, indent=2)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):  # auto-fix agar dict nikla
        data = [data]
        save_users(data)
    return data

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- Bad Words List ---
BAD_WORDS = [
    "bc", "mc", "taxi", "bhenchod", "madarchod", "chadarmod",
    "bhen ka loda", "ghasti", "uc", "ac", "pagal",
    "maa ka phuda", "bhen ko lund", "jahil"
]

# --- Conversation States ---
NAME, CITY, GENDER, CHOICE_CITY, PHOTO, CONTACT = range(6)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📝 Register", "❤️ Find Match"],
        ["ℹ️ Help", "👤 My Profile"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Welcome dost!\n\nYe matchmaking bot 💘 apko new dosti aur relationships ke liye help karega.\n"
        "Bas register karo aur apna match dhundo 🚀",
        reply_markup=reply_markup
    )

# --- Registration Flow ---
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✍️ Apna full name likho dost:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    # Show fixed cities
    keyboard = [[city] for city in CITY_OPTIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🏙️ Ap kis city se ho? Sirf options me se select karo:", reply_markup=reply_markup)
    return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text not in CITY_OPTIONS:
        await update.message.reply_text("⚠️ Dost sirf given options me se select karo.")
        return CITY
    context.user_data["city"] = update.message.text
    await update.message.reply_text("🚻 Apka gender kya hai? (Male/Female):")
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text.capitalize()
    keyboard = [[city] for city in CITY_OPTIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("💡 Apko kis city ki match pasand hogi?", reply_markup=reply_markup)
    return CHOICE_CITY

async def get_choice_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text not in CITY_OPTIONS:
        await update.message.reply_text("⚠️ Dost sirf given options me se select karo.")
        return CHOICE_CITY
    context.user_data["choice_city"] = update.message.text
    await update.message.reply_text("📸 Apni picture bhejo (sirf match ke waqt show hogi).")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    context.user_data["photo"] = photo_file.file_id
    keyboard = [[KeyboardButton("📱 Share Contact", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📱 Apna WhatsApp number ya Telegram ID bhejo:", reply_markup=reply_markup)
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:  # agar user "Share Contact" kare
        contact_info = update.message.contact.phone_number
    else:
        contact_info = update.message.text.strip()

    context.user_data["contact"] = contact_info

    users = load_users()
    users.append({
        "id": update.message.from_user.id,
        "name": context.user_data["name"],
        "city": context.user_data["city"],
        "gender": context.user_data["gender"],
        "choice_city": context.user_data["choice_city"],
        "photo": context.user_data["photo"],
        "contact": context.user_data["contact"],
        "unlocked": False,
        "matched": None
    })
    save_users(users)

    await update.message.reply_text("✅ Registration complete hogayi dost! Ab ap /find try kar sakte ho 💘")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Registration cancel hogayi.")
    return ConversationHandler.END

# --- Find Match ---
async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = update.message.from_user.id
    me = next((u for u in users if u["id"] == user_id), None)

    if not me:
        await update.message.reply_text("⚠️ Dost pehle /register karlo.")
        return

    # If already matched
    if me.get("matched"):
        match = next((u for u in users if u["id"] == me["matched"]), None)
    else:
        matches = [
            u for u in users if u["gender"] != me["gender"] and
            (u["city"].lower() == me["choice_city"].lower() or u["city"].lower() == me["city"].lower())
        ]
        if not matches:
            await update.message.reply_text("❌ Abhi koi match available nahi dost, thori der baad try karo.")
            return
        match = random.choice(matches)
        me["matched"] = match["id"]
        save_users(users)

    compatibility = random.randint(70, 95)

    if me.get("unlocked"):
        await update.message.reply_photo(
            match["photo"],
            caption=(f"💘 Match Mil Gayi!\n\n"
                     f"👤 Name: {match['name']}\n"
                     f"🏙️ City: {match['city']}\n"
                     f"❤️ Compatibility: {compatibility}%\n\n"
                     f"📱 Contact: {match['contact']}")
        )
    else:
        await update.message.reply_photo(
            match["photo"],
            caption=(f"💘 Match Mil Gayi!\n\n"
                     f"👤 Name: {match['name']}\n"
                     f"🏙️ City: {match['city']}\n"
                     f"❤️ Compatibility: {compatibility}%\n\n"
                     f"🔒 Contact info lock hai.\n"
                     f"Unlock karne ke liye Rs.500 Easypaisa bhejein: 03480223684 (Talha Mehmood)\n\n"
                     f"Payment proof bhejne ke baad receipt forward karein @{ADMIN_USERNAME} ko.")
        )

# --- Profile ---
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    me = next((u for u in users if u["id"] == update.message.from_user.id), None)

    if not me:
        await update.message.reply_text("⚠️ Dost ap register nahi ho. Use /register.")
        return

    await update.message.reply_text(
        f"👤 Apki Profile:\n\n"
        f"Name: {me['name']}\nCity: {me['city']}\nGender: {me['gender']}\n"
        f"Choice City: {me['choice_city']}\nContact: {me['contact']}\n"
        f"Unlocked: {me['unlocked']}"
    )

# --- Help ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Commands dost:\n\n"
        "/register - Register karo\n"
        "/find - Match dhundo\n"
        "/profile - Apni profile dekho\n"
        "/help - Ye message"
    )

# --- Moderation / Unlock ---
async def moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Dost ap admin nahi ho.")
        return

    users = load_users()
    text = "👥 Registered Users:\n\n"
    for u in users:
        text += f"{u['id']} | {u['name']} | {u['city']} | {u['gender']} | {u['contact']} | Unlocked: {u['unlocked']}\n"
    await update.message.reply_text(text or "No users yet.")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sirf admin unlock kar sakta hai.")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("⚠️ Usage: /unlock <user_id>")
        return

    users = load_users()
    me = next((u for u in users if u["id"] == user_id), None)
    if not me:
        await update.message.reply_text("⚠️ User nahi mila.")
        return

    me["unlocked"] = True
    save_users(users)
    await update.message.reply_text(f"✅ User {user_id} unlock kar diya gaya.")
    
# --- Bad Word Filter ---
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for bad in BAD_WORDS:
        if bad in text:
            try:
                await update.message.delete()
            except:
                pass
            user = update.message.from_user
            name = f"@{user.username}" if user.username else user.first_name
            await update.message.chat.send_message(f"⚠️ Gali mat do dost, {name}!")
            return

# --- Main Function ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 Register$"), register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            CHOICE_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_choice_city)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact),
                MessageHandler(filters.CONTACT, get_contact)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("find", find_match))
    app.add_handler(CommandHandler("moderation", moderation))
    app.add_handler(CommandHandler("unlock", unlock))

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^❤️ Find Match$"), find_match))
    app.add_handler(MessageHandler(filters.Regex("^👤 My Profile$"), profile))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ Help$"), help_command))

    # Bad word filter
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_bad_words))

    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
