import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

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

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"balance": 100}  # test balance
        save_users(users)

    keyboard = [
        [InlineKeyboardButton("💵 Balance", callback_data="balance")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🎮 Play Game", url="https://your-site.netlify.app")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎉 Welcome to Bingo Cash System",
        reply_markup=reply_markup
    )

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    if query.data == "balance":
        bal = users[user_id]["balance"]
        await query.edit_message_text(f"💰 Your balance: {bal} birr")

    elif query.data == "withdraw":
        context.user_data["withdraw"] = True
        await query.edit_message_text("💸 Enter amount to withdraw:")

    elif query.data.startswith("approve"):
        _, uid, amount = query.data.split("_")

        users[uid]["balance"] -= int(amount)
        save_users(users)

        await context.bot.send_message(uid, f"✅ Withdraw Approved: {amount} birr")
        await query.edit_message_text("✅ Approved")

    elif query.data.startswith("reject"):
        _, uid = query.data.split("_")

        await context.bot.send_message(uid, "❌ Withdraw Rejected")
        await query.edit_message_text("❌ Rejected")

# ================= HANDLE TEXT =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if context.user_data.get("withdraw"):
        amount = int(update.message.text)

        if amount > users[user_id]["balance"]:
            await update.message.reply_text("❌ Not enough balance")
            return

        # send to admin
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_{amount}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💸 Withdraw Request\nUser: {user_id}\nAmount: {amount}",
            reply_markup=reply_markup
        )

        await update.message.reply_text("⏳ Request sent to admin")

        context.user_data["withdraw"] = False

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")

app.run_polling()
