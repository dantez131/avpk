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

LOG_CHAT_ID = -1003671787625

BASE_APP_URL = "https://aviatorsbot.up.railway.app/"

user_status = {}
USERS_FILE = "users.json"

# ===========================
# LOAD & SAVE USERS
# ===========================

def load_users():
    global user_status
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_status = {int(k): v for k, v in data.items()}
        print(f"📂 Loaded users from {USERS_FILE}: {user_status}")
    except Exception as e:
        print(f"⚠️ Could not load {USERS_FILE}: {e}")
        user_status = {}

def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in user_status.items()}, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved statuses to {USERS_FILE}")
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
# MAIN MENU KEYBOARD
# ===========================

def menu_keyboard(user_id: int):
    status = user_status.get(user_id, "new")

    buttons = [
        [InlineKeyboardButton("📖 Connection & Usage Guide", callback_data="instruction")],
        [InlineKeyboardButton("🤖 Connect Bot", callback_data="connect")],
        [InlineKeyboardButton("💸 Price", callback_data="price")],
        [InlineKeyboardButton(
            "🆘 Help",
            url="https://t.me/Dante_Valdes?text=Hi!%20I%20have%20a%20question%20about%20the%20bot"
        )],
    ]

    if status == "new":
        url = f"{BASE_APP_URL}?screen=noreg"
        label = "Open Aviator Predictor"
    elif status == "registered":
        url = f"{BASE_APP_URL}?screen=nodep"
        label = "Open Aviator Predictor"
    else:
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
        f"User {user_id} pressed button: /start (status: {user_status[user_id]})"
    )

    await update.message.reply_text(
        "👋 Hi! This is the main menu of the bot.\n"
        "All actions are available in the buttons below 👇",
        reply_markup=menu_keyboard(user_id),
    )

# ===========================
# CALLBACK HANDLER
# ===========================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await query.answer()
    status = user_status.get(user_id, "new")

    if data == "instruction":
        await send_log(context.application, f"User {user_id} pressed button: GUIDE")

        await query.edit_message_text(
            "1 - Bot Connection:\n"
            "Create a new account and wait about 1 minute for the bot to detect it, "
            "then make a deposit and wait another 2 minutes for synchronization.\n\n"
            "2 - Using the bot:\n"
            "When the round starts, press GET COEFFICIENT. "
            "You will receive the coefficient at which the plane will fly away in THIS round.",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "connect":
        await send_log(context.application, f"User {user_id} pressed button: CONNECT BOT")

        if status == "new":
            text = "Create a new account. Once created, you will automatically receive a notification and instructions for the bot."

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 CREATE ACCOUNT", url=f"https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}")],
                [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard)

        elif status == "registered":
            text = "✅ Account detected. Please make a deposit to continue. $5 is required to properly synchronize the bot."

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 MAKE A DEPOSIT", url=f"https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}")],
                [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
