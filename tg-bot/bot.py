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

LOG_CHAT_ID = -1003671787625  # чат для логов
POSTBACK_CHAT_ID = -1003712583340  # чат с постбеками
PUSH_CHAT_ID = -1003889323542  # <-- ДОБАВЛЕНО: чат для пушей

BASE_APP_URL = "https://aviatorbot.up.railway.app/"

ID_PATTERN = re.compile(r"==(\d+)==")

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
# КЛИКАБЕЛЬНЫЙ ID (БЕЗ КАРТОЧКИ)
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
# УНИВЕРСАЛЬНОЕ INLINE-МЕНЮ
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
# ОБРАБОТКА INLINE-КНОПОК
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
            "Devi creare un nuovo account e attendere circa 1 minuto finché il bot lo rileva. "
            "Poi effettua un deposito e attendi altri 2 minuti per la sincronizzazione.\n\n"
            "2 - Utilizzo del bot:\n"
            "Quando inizia il round, premi il pulsante Mostra.",
            reply_markup=menu_keyboard(user_id),
        )

# ===========================
# ОБРАБОТКА ПОСТБЕКОВ
# ===========================

async def postback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != POSTBACK_CHAT_ID:
        return

    text = update.message.text or ""
    match = ID_PATTERN.search(text)

    if not match:
        await send_log(context.application, f"⚠️ Постбек без понятного ID: {text}")
        return

    user_id = int(match.group(1))
    user_status.setdefault(user_id, "new")

    text_lower = text.lower()

    if "registration" in text_lower or "reg" in text_lower:
        user_status[user_id] = "registered"
        save_users()
        await send_log(context.application, f"📩 Регистрация для [{user_id}](tg://user?id={user_id})")

    elif "deposit" in text_lower or "amount" in text_lower:
        user_status[user_id] = "deposited"
        save_users()
        await send_log(context.application, f"💰 Депозит для [{user_id}](tg://user?id={user_id})")

# ===========================
# PUSH HANDLER (ДОБАВЛЕНО)
# ===========================

async def push_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != PUSH_CHAT_ID:
        return

    text = update.message.text or ""

    if not text.startswith("ПУШ"):
        return

    match = re.search(r"ПУШ\s*\((.*?)\)\s*\"(.*?)\"", text)
    if not match:
        await send_log(context.application, f"❌ Неверный формат PUSH: {text}")
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
            await context.application.bot.send_message(
                chat_id=user_id,
                text=push_text
            )
            sent += 1
        except Exception as e:
            failed += 1

    await send_log(
        context.application,
        f"📢 PUSH выполнен | Отправлено: {sent} | Ошибок: {failed}"
    )

# ===========================
# ЗАПУСК БОТА
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

    app.add_handler(
        MessageHandler(filters.Chat(PUSH_CHAT_ID) & filters.TEXT, push_handler)
    )

    print("✅ Bot started and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
