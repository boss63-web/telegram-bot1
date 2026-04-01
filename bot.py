import json
import os
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

GAME_URL = "https://ahmedsgame.netlify.app/"

# ================= DATABASE =================
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

users = load_users()

# ================= TEXT =================
texts = {
    "en": {
        "welcome": "🎉 Welcome to Bingo Cash Games!\n\nChoose your language:",
        "ask_phone": "📱 Please share your phone number:",
        "bonus": "🎁 You received 10 Birr bonus!",
        "already": "❌ This phone is already registered.",
        "done": "✅ Registration complete!",
        "play": "Play Game"
    },
    "am": {
        "welcome": "🎉 እንኳን ወደ Bingo Cash Games በደህና መጡ!\n\nቋንቋ ይምረጡ:",
        "ask_phone": "📱 እባክዎን ስልክ ቁጥር ያጋሩ:",
        "bonus": "🎁 10 ብር ቦነስ ተቀብለዋል!",
        "already": "❌ ይህ ቁጥር ቀድሞ ተመዝግቧል።",
        "done": "✅ ተመዝግቧል!",
        "play": "ጫወታ ጀምር"
    },
    "or": {
        "welcome": "🎉 Baga gara Bingo Cash Games dhuftan!\n\nAfaan filadhaa:",
        "ask_phone": "📱 Lakkoofsa bilbilaa keessan nuuf kennaa:",
        "bonus": "🎁 10 Birr bonasii argattan!",
        "already": "❌ Lakkoofsi kun duraan galmaa'eera.",
        "done": "✅ Galmeen xumurameera!",
        "play": "Taphi jalqabi"
    },
    "ti": {
        "welcome": "🎉 እንቋዕ ናብ Bingo Cash Games ብደሓን መጻእኩም!\n\nቋንቋ ምረጹ:",
        "ask_phone": "📱 በጃኹም ቁጽሪ ስልኪኹም ኣቕርቡ:",
        "bonus": "🎁 10 ብር ቦነስ ተቐቢልኩም!",
        "already": "❌ እዚ ቁጽሪ ኣቐዲሙ ተመዝጊቡ እዩ።",
        "done": "✅ ምዝገባ ተዛዚሙ!",
        "play": "ጸወታ ጀምር"
    }
}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("አማርኛ", callback_data="lang_am")],
        [InlineKeyboardButton("Afaan Oromo", callback_data="lang_or")],
        [InlineKeyboardButton("ትግርኛ", callback_data="lang_ti")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎉 Welcome to Bingo Cash Games!\n\n🌍 Choose your language:",
        reply_markup=reply_markup
    )

# ================= LANGUAGE =================
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[1]
    user_id = str(query.from_user.id)

    if user_id not in users:
        users[user_id] = {"language": lang, "balance": 0, "phone": None}
    else:
        users[user_id]["language"] = lang

    save_users(users)

    msg = texts[lang]["ask_phone"]

    contact_btn = KeyboardButton("📱 Share Phone", request_contact=True)
    keyboard = [[contact_btn]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await query.message.reply_text(msg, reply_markup=reply_markup)

# ================= PHONE =================
async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in users:
        return

    phone = update.message.contact.phone_number
    lang = users[user_id]["language"]

    # check duplicate
    for uid in users:
        if users[uid].get("phone") == phone and uid != user_id:
            await update.message.reply_text(texts[lang]["already"])
            return

    # save phone + give bonus
    users[user_id]["phone"] = phone
    users[user_id]["balance"] = users[user_id].get("balance", 0) + 10
    save_users(users)

    # ✅ Bottom Play Button
    play_btn = KeyboardButton(f"🎮 {texts[lang]['play']}")
    keyboard = [[play_btn]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"{texts[lang]['bonus']}\n\n{texts[lang]['done']}",
        reply_markup=reply_markup
    )

# ================= PLAY BUTTON HANDLER =================
async def play_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        return

    lang = users[user_id]["language"]

    await update.message.reply_text(
        f"🎮 {texts[lang]['play']}\n{GAME_URL}"
    )

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(language, pattern="lang_"))
app.add_handler(MessageHandler(filters.CONTACT, phone_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🎮"), play_handler))

app.run_polling()
