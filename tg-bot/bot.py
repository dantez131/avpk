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
        [InlineKeyboardButton("📖 Istruzioni per il collegamento e il funzionamento", callback_data="instruction")],
        [InlineKeyboardButton("🤖 Connetti un bot", callback_data="connect")],
        [InlineKeyboardButton("💸 Prezzo", callback_data="price")],
        [InlineKeyboardButton(
            "🆘 Fai una domanda",
            url="https://t.me/Dante_Valdes?text=Ciao!%20Ho%20una%20domanda%20sul%20bot"
        )],
    ]

    if status == "new":
        url = f"{BASE_APP_URL}?screen=noreg"
        label = "Apri Aviator Predittore"
    elif status == "registered":
        url = f"{BASE_APP_URL}?screen=nodep"
        label = "Apri Aviator Predittore"
    else:  # deposited
        url = BASE_APP_URL
        label = "🚀 Apri Aviator Predittore"

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
        "👋 Ciao! Questo è il menu principale del bot.\n"
        "Tutte le azioni sono disponibili nei pulsanti sottostanti 👇",
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
        text="✅ Account rilevato dal bot! \n Ora effettua un deposito per connetterti.\n"
             "Il deposito minimo è di soli 20 euro affinché il bot si connetta al tuo account.",
        reply_markup=menu_keyboard(user_id),
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 HO EFFETTUATO UN DEPOSITO", callback_data="made_deposit")],
        [InlineKeyboardButton("⬅️ Torna al menù", callback_data="back_menu")]
    ])

    await app.bot.send_message(
        chat_id=user_id,
        text="✅ Account rilevato dal bot! \n Ora effettua un deposito per connetterti.\n"
             "Il deposito minimo è di soli 20 euro affinché il bot si connetta al tuo account.",
        reply_markup=menu_keyboard(user_id),
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 HO EFFETTUATO UN DEPOSITO", callback_data="made_deposit")],
        [InlineKeyboardButton("⬅️ Torna al menù", callback_data="back_menu")]
    ])

    await send_log(app, f"✅ Статус {user_id} → registered")

async def process_deposit(app: Application, user_id: int):
    await asyncio.sleep(190)

    user_status[user_id] = "deposited"
    save_users()

    await app.bot.send_message(
        chat_id=user_id,
        text="🎉 Deposito rilevato! Bot connesso correttamente.\n"
             "Ora puoi aprire l'applicazione e iniziare a giocare 🚀",
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
            "1 - Connessione di un bot:\n"
            "Devi creare un nuovo account e attendere circa 1 minuto affinché il bot lo rilevi, "
            "quindi effettua un deposito e attendi altri 2 minuti affinché il bot si sincronizzi. "
            "Il bot è connesso e pronto a funzionare.\n\n"
            "2 - Utilizzando il bot:\n"
            "Non appena inizia il round, premi il pulsante MOSTRA COEFFICIENTE. "
            "Riceverai le quote sulle quali l'aereo volerà via in QUESTO round",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "connect":

        if status == "new":
            text = (
                "Quando crei un account sul sito, fai clic sul pulsante per connettere il bot ✅\n\n"
                "👉 [CREARE UN ACCOUNT](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}) 👈"
            ).format(user_id=user_id)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 CREO UN ACCOUNT", callback_data="created_account")],
                [InlineKeyboardButton("⬅️ Torna al menù", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

        elif status == "registered":
            text = (
                "✅ Account trovato dal bot. Ora effettua un deposito per connetterti.\n\n"
                "👉 [EFFETTUARE UN DEPOSITO](https://gembl.pro/click?o=780&a=1933&sub_id2={user_id}) 👈"
            ).format(user_id=user_id)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 HO EFFETTUATO UN DEPOSITO", callback_data="made_deposit")],
                [InlineKeyboardButton("⬅️ Torna al menù", callback_data="back_menu")]
            ])

            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

        else:  # deposited
            await query.edit_message_text(
                "✅ Il bot è connesso e pronto a funzionare.",
                reply_markup=menu_keyboard(user_id),
            )

    elif data == "price":
        await query.edit_message_text(
            "Il bot è completamente gratuito. Credo nella bontà e nell'onestà delle persone. "
            "Se vuoi condividere parte della tua vincita scrivimi e ti invierò i dettagli per il bonifico. Grazie!",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "back_menu":
        await query.edit_message_text(
            "Menù principale 👇",
            reply_markup=menu_keyboard(user_id),
        )

    elif data == "created_account":
        await query.edit_message_text(
            "🔍 Il bot sta cercando il tuo account, attendi 1-2 minuti. "
            "Una volta trovato l'account, riceverai una notifica..."
        )

        await send_log(context.application, f"⏳ Пользователь {user_id} нажал: Я СОЗДАЛ АККАУНТ")

        asyncio.create_task(process_registration(context.application, user_id))

    elif data == "made_deposit":
        await query.edit_message_text(
            "🔄 Il bot si sta connettendo al tuo account, attendi 1-3 minuti..."
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
