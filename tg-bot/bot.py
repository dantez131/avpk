import os
import re
import json
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ===========================
# SETTINGS
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG_CHAT_ID = -1003671787625       # chat for logs

BASE_APP_URL = "https://aviatorsbot.up.railway.app/"

user_status = {}
USERS_FILE = "users.json"

# ===========================
# LOAD AND SAVE STATUSES
# ===========================

def load_users():
    global user_status
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_status = {int(k): v for k, v in data.items()}
        print(f"📂 Loaded users from {USERS_FILE}: {user_status}")
    except Exception as e:
        print(f"⚠️ Failed to load {USERS_FILE}: {e}")
        user_status = {}

def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in user_status.items()}, f, ensure_ascii=False, indent=2)
        print(f"💾 Statuses saved to {USERS_FILE}")
    except Exception as e:
        print(f"❌ Error saving users.json: {e}")

# ===========================
# LOGS
# ===========================

async def send_log(app: Application, text: str):
    try:
        await app.bot.send_message(chat_id=LOG_CHAT_ID, text=f"📡 LOG: {text}")
    except Exception as e:
        print(f"Logging error: {e}")

# ===========================
# UNIVERSAL INLINE MENU
# ===========================

def menu_keyboard(user_id: int):
    status = user_status.get(user_id, "new")

    buttons = [
        [InlineKeyboardButton("📖 Instructions for connection and usage", callback_data="instruction")],
        [InlineKeyboardButton("🤖 Connect a bot", callback_data="connect")],
        [InlineKeyboardButton("💸 Price", callback_data="price")],
        [InlineKeyboardButton(
            "🆘 Ask a question",
            url="https://t.me/Dante_Valdes?text=Hi!%20I%20have%20a%20question%20about%20the%20bot"
        )],
    ]

    if status == "new":
        url = f"{BASE_APP_URL}?screen=noreg"
        label = "Open Aviator Predictor"
    elif status == "registered":
        url = f"{BASE_APP_URL}?screen=nodep"
        label = "Open Aviator Predictor"
    else:  # deposited
        url = BASE_APP_URL
        label = "🚀 Open Aviator Predictor"

    buttons.append([InlineKeyboardButton(label, web_app=WebAppInfo(url=url))])

    return InlineKeyboardMarkup(buttons)

# ===========================
# /START
# ===========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_status.setdefault(user_id, "new")
    save_users()

    await send_log(
        context.application,
        f"User {user_id} pressed: /start (status: {user_status[user_id]})"
    )

    await update.message.reply_text(
        "👋 Hi! This is the main menu of the bot.\n"
        "All actions are available in the buttons below 👇",
        reply_markup=menu_keyboard(user_id),
    )

# ===========================
# INLINE BUTTON HANDLER
# ===========================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await query.answer()
    status = user_status.get(user_id, "new")

    if data == "instruction":
        await send_log(context.application, f"User {user_id} pressed: INSTRUCTIONS")

        await query.edit_message_text(
            "1 - Connecting a bot:\n"
            "You need to create a new account and wait about 1 minute for the bot to detect it, "
            "then make a deposit and wait another 2 minutes for the bot to sync. "
            "The bot is connected and ready to work.\n\n"
            "2 - Using the bot:\n"
            "As soon as the round starts, press the SHOW COEFFICIENT button. "
            "You will receive the odds on which the plane will fly in THIS round",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "connect":
        await send_log(context.application, f"User {user_id} pressed: CONNECT A BOT")

        if status == "new":
            text = (
                "When creating an account on the site, click the button to connect the bot ✅"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 CREATE ACCOUNT", url=f"https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}")],
                [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard)

        elif status == "registered":
            text = (
                "✅ Account found by the bot. Now make a deposit to connect."
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 MAKE A DEPOSIT", url=f"https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}")],
                [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard)

        else:  # deposited
            await query.edit_message_text(
                "✅ The bot is connected and ready to work.",
                reply_markup=menu_keyboard(user_id),
            )

    elif data == "price":
        await send_log(context.application, f"User {user_id} pressed: PRICE")

        await query.edit_message_text(
            "The bot is completely free. I believe in people's kindness and honesty. "
            "If you want to share part of your winnings, write to me and I will send you the details for the transfer. Thank you!",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "back_menu":
        await send_log(context.application, f"User {user_id} pressed: BACK TO MENU")

        await query.edit_message_text(
            "Main menu 👇",
            reply_markup=menu_keyboard(user_id),
        )

# ===========================
# START BOT
# ===========================

def main():
    print("🚀 Starting the bot...")

    load_users()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback))

    print("✅ Bot started and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
