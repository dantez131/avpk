import os
import re
import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ===========================
# НАСТРОЙКИ
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG_CHAT_ID = -1003671787625
POSTBACK_CHAT_ID = -1003712583340

BASE_APP_URL = "https://aviatorbot.up.railway.app/"

ID_PATTERN = re.compile(r"==(\d+)==")
PUSH_PATTERN = re.compile(r"ПУШ\s*\((.*?)\)\s*\"(.*?)\"", re.IGNORECASE)

user_status = {}
USERS_FILE = "users.json"

# ===========================
# ЗАГРУЗКА И СОХРАНЕНИЕ
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
# КЛИКАБЕЛЬНЫЙ ID
# ===========================

def clickable_user(user):
    return f"[{user.id}](tg://user?id={user.id})"

# ===========================
# ЛОГИ
# ===========================

async def send_log(app: Application, text: str):
    try:
        await app.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=f"📡 LOG: {text}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка логирования: {e}")

# ===========================
# МЕНЮ
# ===========================

def menu_keyboard(user_id: int):
    status = user_status.get(user_id, "new")

    buttons = [
        [InlineKeyboardButton("📖 Istruzioni per la connessione e l’utilizzo", callback_data="instruction")],
        [InlineKeyboardButton("🤖 Collega il bot", callback_data="connect")],
        [InlineKeyboardButton("💸 Prezzo", callback_data="price")],
        [InlineKeyboardButton(
            "🆘 Assistenza",
            url="https://t.me/Dante_Valdes?text=Ciao!%20Ho%20una%20domanda%20sul%20bot"
        )],
    ]

    if status == "new":
        url = f"{BASE_APP_URL}?screen=noreg"
        label = "🔒 Apri l’app (in attesa della registrazione)"
    elif status == "registered":
        url = f"{BASE_APP_URL}?screen=nodep"
        label = "⏳ Apri l’app (in attesa del deposito)"
    else:
        url = BASE_APP_URL
        label = "🚀 Apri l’app (accesso attivo)"

    buttons.append([InlineKeyboardButton(label, web_app=WebAppInfo(url=url))])

    return InlineKeyboardMarkup(buttons)

# ===========================
# /START
# ===========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_status.setdefault(user_id, "new")
    save_users()

    await send_log(
        context.application,
        f"Пользователь {clickable_user(user)} нажал /start (статус: {user_status[user_id]})"
    )

    await update.message.reply_text(
        "👋 Ciao! Questo è il menu principale del bot.\n"
        "Tutte le funzioni sono disponibili nei pulsanti qui sotto 👇",
        reply_markup=menu_keyboard(user_id),
    )

# ===========================
# INLINE-КНОПКИ
# ===========================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    data = query.data

    await query.answer()
    status = user_status.get(user_id, "new")

    await send_log(
        context.application,
        f"Пользователь {clickable_user(user)} нажал кнопку '{data}' (статус: {status})"
    )

    if data == "instruction":
        await query.edit_message_text(
            "1 - Connessione del bot:\n"
            "Crea un nuovo account e attendi circa 1 minuto.\n"
            "Poi effettua un deposito e attendi 2 minuti per la sincronizzazione.\n\n"
            "2 - Utilizzo del bot:\n"
            "Quando inizia il round, premi Mostra.",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "connect":
        if status == "new":
            text = (
                f"Crea un account.\n"
                f"[CREA ACCOUNT](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id})"
            )
        elif status == "registered":
            text = (
                f"✅ Account rilevato.\n"
                f"[CONTINUA](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id})"
            )
        else:
            text = (
                f"✅ Bot collegato.\n"
                f"[APRI IL GIOCO](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id})"
            )

        await query.edit_message_text(
            text,
            reply_markup=menu_keyboard(user_id),
            parse_mode="Markdown"
        )

# ===========================
# ПОСТБЕК + PUSH
# ===========================

async def postback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text.strip()

    # ==============================
    # 🔥 1. ОБРАБОТКА ПУШ КОМАНДЫ
    # ==============================
    if text.startswith("ПУШ"):
        import re

        match = re.search(r"ПУШ\s*\((.*?)\)\s*\"(.*?)\"", text)
        if not match:
            await context.bot.send_message(
                chat_id=LOG_CHAT_ID,
                text=f"❌ Неверный формат ПУШ:\n{text}"
            )
            return

        ids_raw = match.group(1)
        push_text = match.group(2)

        user_ids = []
        for uid in ids_raw.split(","):
            uid = uid.strip()
            if uid.isdigit():
                user_ids.append(int(uid))

        sent = 0
        failed = 0

        for user_id in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=push_text
                )
                sent += 1
            except:
                failed += 1

        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=(
                f"📢 PUSH выполнен\n"
                f"Отправлено: {sent}\n"
                f"Ошибок: {failed}"
            )
        )
        return

    # ==============================
    # 🔹 2. ОБЫЧНЫЕ ПОСТБЕКИ
    # ==============================

    import re
    match = re.search(r"\d+", text)

    if not match:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=f"⚠️ Постбек без понятного ID: {text}"
        )
        return

    user_id = int(match.group())

    users = load_users()
    user = users.get(str(user_id))

    if not user:
        users[str(user_id)] = {
            "registered": False,
            "deposits": 0
        }
        user = users[str(user_id)]

    # REGISTRATION
    if "Registration" in text:
        user["registered"] = True
        save_users(users)

        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=f"✅ Регистрация: {user_id}"
        )
        return

    # DEPOSIT
    if "Deposit" in text:
        user["deposits"] += 1
        save_users(users)

        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=f"💰 Депозит: {user_id} | Всего: {user['deposits']}"
        )
        return

    await context.bot.send_message(
        chat_id=LOG_CHAT_ID,
        text=f"⚠️ Неизвестный постбек: {text}"
    )
# ===========================
# ЗАПУСК
# ===========================

def main():
    print("🚀 Бот запускается...")

    load_users()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(
        MessageHandler(filters.Chat(POSTBACK_CHAT_ID) & filters.TEXT, postback_handler)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
