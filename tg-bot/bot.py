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
# НАСТРОЙКИ
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG_CHAT_ID = -1003671787625       # чат для логов

BASE_APP_URL = "https://aviatorbot.up.railway.app/"

user_status = {}
USERS_FILE = "users.json"

# ===========================
# ЗАГРУЗКА И СОХРАНЕНИЕ СТАТУСОВ
# ===========================

def load_users():
    global user_status
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_status = {int(k): v for k, v in data.items()}
        print(f"📂 Загружены пользователи из {USERS_FILE}: {user_status}")
    except Exception as e:
        print(f"⚠️ Не удалось загрузить {USERS_FILE}: {e}")
        user_status = {}

def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in user_status.items()}, f, ensure_ascii=False, indent=2)
        print(f"💾 Статусы сохранены в {USERS_FILE}")
    except Exception as e:
        print(f"❌ Ошибка сохранения users.json: {e}")

# ===========================
# ЛОГИ
# ===========================

async def send_log(app: Application, text: str):
    try:
        await app.bot.send_message(chat_id=LOG_CHAT_ID, text=f"📡 LOG: {text}")
    except Exception as e:
        print(f"Ошибка логирования: {e}")

# ===========================
# УНИВЕРСАЛЬНОЕ INLINE-МЕНЮ
# ===========================

def menu_keyboard(user_id: int):
    status = user_status.get(user_id, "new")

    buttons = [
        [InlineKeyboardButton("📖 Instructions for connection and using", callback_data="instruction")],
        [InlineKeyboardButton("🤖 Connect a bot", callback_data="connect")],
        [InlineKeyboardButton("💸 Price", callback_data="price")],
        [InlineKeyboardButton(
            "🆘 Help",
            url="https://t.me/Dante_Valdes?text=Hi!%20can%20you%20help%20me%20with%20bot?"
        )],
    ]

    if status == "new":
        url = f"{BASE_APP_URL}?screen=noreg"
        label = "Launch Predictor bot"
    elif status == "registered":
        url = f"{BASE_APP_URL}?screen=nodep"
        label = "Launch Predictor bot"
    else:  # deposited
        url = BASE_APP_URL
        label = "🚀 Launch Predictor bot"

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
        f"Пользователь {user_id} нажал /start (статус: {user_status[user_id]})"
    )

    await update.message.reply_text(
        "👋 Hi! Using the bot guarantees a 40x return in at least 20 minutes.  \n"
        "Instructions and how to connect to the bot are in the buttons below.👇",
        reply_markup=menu_keyboard(user_id),
    )

# ===========================
# ФОНОВЫЕ ЗАДАЧИ (НЕ БЛОКИРУЮТ БОТА)
# ===========================

async def process_registration(app: Application, user_id: int):
    await asyncio.sleep(50)

    user_status[user_id] = "registered"
    save_users()

    await app.bot.send_message(
        chat_id=user_id,
        text="✅ The bot has detected an account. Make a deposit to activate the bot.\n"
             "$5 minimum. You can deposit any amount, but it must be more than $5.",
        reply_markup=menu_keyboard(user_id),
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 I MADE A DEPOSIT", callback_data="made_deposit")],
        [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
    ])

    await app.bot.send_message(
        chat_id=user_id,
        text="✅ The bot has detected an account. Make a deposit to activate the bot.\n"
             "$5 minimum. You can deposit any amount, but it must be more than $5.",
        reply_markup=menu_keyboard(user_id),
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 I MADE A DEPOSIT", callback_data="made_deposit")],
        [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
    ])

    await send_log(app, f"✅ Статус {user_id} → registered")

async def process_deposit(app: Application, user_id: int):
    await asyncio.sleep(190)

    user_status[user_id] = "deposited"
    save_users()

    await app.bot.send_message(
        chat_id=user_id,
        text="🎉 Deposit detected! Bot successfully connected.\n"
             "Now you can open the Predictor and start playing.🚀",
        reply_markup=menu_keyboard(user_id),
    )

    await send_log(app, f"💰 Статус {user_id} → deposited")

# ===========================
# ОБРАБОТКА INLINE-КНОПОК
# ===========================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await query.answer()
    status = user_status.get(user_id, "new")

    if data == "instruction":
        await query.edit_message_text(
            "1 - Connecting the Predictor:\n"
            "Create a new account and wait for the Predictor to detect it (about 1 minute), "
            "Make a deposit and wait for the Predictor to recognize it and complete the connection (2 minutes). "
            "The Predictor is connected and ready to work.\n\n"
            "2 - Using the Predictor:\n"
            "Once the round starts, click the GET COEFFICIENT button. "
            "You will receive the coefficient at which the plane will fly away in THIS round.",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "connect":

        if status == "new":
            text = (
                "Create a new account so that Predictor can connect to it.✅\n\n"
                "👉 [CREATE ACCOUNT](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}) 👈"
            ).format(user_id=user_id)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 I'M FINISHED WITH CREATING ACCOUNT", callback_data="created_account")],
                [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

        elif status == "registered":
            text = (
                "✅ The account was found by a Predictor. Now make a deposit to connect it and start use.\n\n"
                "👉 [MAKE A DEPOSIT](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}) 👈"
            ).format(user_id=user_id)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 I SUCCESSFULLY MAKED A DEPOSIT", callback_data="made_deposit")],
                [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

        else:  # deposited
            await query.edit_message_text(
                "✅ The Predictor is connected and ready to work.",
                reply_markup=menu_keyboard(user_id),
            )

    elif data == "price":
        await query.edit_message_text(
            "The Predictor bot is completely free. I believe in the kindness and honesty of people.. "
            "If you'd like to share some of your winnings, please message me and I'll send you the bank transfer details. Thank you!",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "back_menu":
        await query.edit_message_text(
            "Main menu 👇",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "created_account":
        await query.edit_message_text(
            "🔍 The Predictor is searching for your account, please wait 1-2 minutes. "
            "Once the account is found, you will receive a notification...."
        )

        await send_log(context.application, f"⏳ Пользователь {user_id} нажал: Я СОЗДАЛ АККАУНТ")

        asyncio.create_task(process_registration(context.application, user_id))

    elif data == "made_deposit":
        await query.edit_message_text(
            "🔄 The Predictor is connecting to your account, please wait 1-3 minutes..."
        )

        await send_log(context.application, f"⏳ Пользователь {user_id} нажал: Я ВНЕС ДЕПОЗИТ")

        asyncio.create_task(process_deposit(context.application, user_id))

# ===========================
# ЗАПУСК БОТА
# ===========================

def main():
    print("🚀 Il bot si avvia...")

    load_users()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback))

    print("✅ Bot started and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
