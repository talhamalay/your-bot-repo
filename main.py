import os import threading import json from flask import Flask from telegram import Update, ReplyKeyboardMarkup, KeyboardButton from telegram.ext import ( Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes ) import random

--- Flask App for Render ---

flask_app = Flask(name)

@flask_app.route("/") def home(): return "✅ Bot is running fine on Render!"

def run_flask(): port = int(os.environ.get("PORT", 5000)) flask_app.run(host="0.0.0.0", port=port)

--- Bot Token ---

BOT_TOKEN = "8497771770:AAEp8kePJVaurYBL_z-z6lzouJfY22OZhV0" ADMIN_ID = 7053615484   # Only admin can access moderation

--- File for storing users ---

USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE): with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump([], f)

def load_users(): with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_users(data): with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

--- Conversation States ---

NAME, CITY, GENDER, CHOICE_CITY, PHOTO, CONTACT = range(6)

--- Start Command ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [["📝 Register", "❤️ Find Match"], ["ℹ️ Help", "👤 My Profile"]] reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

await update.message.reply_text(
    "👋 Welcome!\n\nThis is a matchmaking bot 💘.\n"
    "Register now to find your perfect match!",
    reply_markup=reply_markup
)

--- Registration ---

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("✍️ Please enter your full name:") return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["name"] = update.message.text await update.message.reply_text("🏙️ Enter your city:") return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["city"] = update.message.text await update.message.reply_text("🚻 Select your gender (Male/Female):") return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["gender"] = update.message.text.capitalize() await update.message.reply_text("💡 Which city do you prefer for your match?") return CHOICE_CITY

async def get_choice_city(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["choice_city"] = update.message.text await update.message.reply_text( "📸 Please send your picture.\n\n⚠️ Note: Picture is only shown during match & then auto-deleted." ) return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE): photo_file = await update.message.photo[-1].get_file() context.user_data["photo"] = photo_file.file_id await update.message.reply_text("📱 Send your WhatsApp number or Telegram ID:") return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["contact"] = update.message.text

# Save to users.json
users = load_users()
users.append({
    "id": update.message.from_user.id,
    "name": context.user_data["name"],
    "city": context.user_data["city"],
    "gender": context.user_data["gender"],
    "choice_city": context.user_data["choice_city"],
    "photo": context.user_data["photo"],
    "contact": context.user_data["contact"]
})
save_users(users)

await update.message.reply_text("✅ Registration completed successfully!")
return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("❌ Registration cancelled.") return ConversationHandler.END

--- Find Match ---

async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE): users = load_users() user_id = update.message.from_user.id me = next((u for u in users if u["id"] == user_id), None)

if not me:
    await update.message.reply_text("⚠️ You need to /register first.")
    return

# Find opposite gender & city match
matches = [u for u in users if u["gender"] != me["gender"] and
           (u["city"].lower() == me["choice_city"].lower() or u["city"].lower() == me["city"].lower())]

if not matches:
    await update.message.reply_text("❌ No match found yet. Try again later.")
    return

match = random.choice(matches)
compatibility = random.randint(60, 95)

await update.message.reply_photo(
    match["photo"],
    caption=(f"💘 Match Found!\n\n"
             f"👤 Name: {match['name']}\n"
             f"🏙️ City: {match['city']}\n"
             f"❤️ Compatibility: {compatibility}%\n\n"
             f"🔒 Contact info is locked.\n"
             f"To unlock pay Rs.500 Easypaisa: 03480223684 (Talha Mehmood)")
)

--- Profile ---

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE): users = load_users() user_id = update.message.from_user.id me = next((u for u in users if u["id"] == user_id), None)

if not me:
    await update.message.reply_text("⚠️ You are not registered. Use /register.")
    return

await update.message.reply_text(
    f"👤 Your Profile:\n\n"
    f"Name: {me['name']}\nCity: {me['city']}\nGender: {me['gender']}\nChoice City: {me['choice_city']}\nContact: {me['contact']}"
)

--- Help ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "ℹ️ Commands:\n\n" "/register - Register yourself\n" "/find - Find a match\n" "/profile - View your profile\n" "/help - Show this message" )

--- Moderation ---

async def moderation(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.from_user.id != ADMIN_ID: await update.message.reply_text("❌ You are not authorized.") return

users = load_users()
text = "👥 Registered Users:\n\n"
for u in users:
    text += f"{u['name']} | {u['city']} | {u['gender']} | {u['contact']}\n"
await update.message.reply_text(text or "No users yet.")

--- Main Function ---

def main(): threading.Thread(target=run_flask, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📝 Register$"), register)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        CHOICE_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_choice_city)],
        PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("find", find_match))
app.add_handler(CommandHandler("moderation", moderation))

app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.Regex("^❤️ Find Match$"), find_match))
app.add_handler(MessageHandler(filters.Regex("^👤 My Profile$"), profile))
app.add_handler(MessageHandler(filters.Regex("^ℹ️ Help$"), help_command))

app.run_polling(drop_pending_updates=True, close_loop=False)

if name == "main": main()

