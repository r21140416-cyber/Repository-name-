import telebot
import schedule
import time
import threading
import json
import os
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '9146697142:AAFrB0_61euCijMy9n7sy8Q29rUVYLE4QtQ'  # ⬅️ توکن خودت رو دقیقاً اینجا بذار (یا همون که هست)
bot = telebot.TeleBot(TOKEN)

DB_FILE = 'users_lang.json'

def load_lang():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_lang(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(
        message.chat.id,
        "👋 Welcome!\nPlease choose your language:\n\n"
        "👋 خوش آمدید!\nلطفاً زبان خود را انتخاب کنید:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang = call.data.split('_')[1]
    data = load_lang()
    data[str(call.message.chat.id)] = lang
    save_lang(data)

    if lang == 'fa':
        bot.edit_message_text("✅ زبان شما روی فارسی تنظیم شد.\n\nبرای تنظیم یادآور بنویسید:\nیادآور 14:30 برو دکتر", call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    else:
        bot.edit_message_text("✅ Language set to English.\n\nType:\nremind 14:30 Go to doctor", call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    data = load_lang()
    user_lang = data.get(str(chat_id), 'fa')

    keyword = "یادآور" if user_lang == 'fa' else "remind"
    error_format = "❌ فرمت اشتباه. مثال: یادآور 14:30 برو دکتر" if user_lang == 'fa' else "❌ Wrong format. Example: remind 14:30 Go to doctor"

    if text.startswith(keyword):
        try:
            parts = text.split(' ', 2)
            if len(parts) < 3:
                bot.reply_to(message, error_format, parse_mode='Markdown')
                return
            
            time_str = parts[1]
            task = parts[2]

            datetime.strptime(time_str, "%H:%M")

            schedule.every().day.at(time_str).do(send_reminder, chat_id=chat_id, task=task, lang=user_lang)
            
            success_msg = f"✅ یادآور تنظیم شد!\n⏰ ساعت: {time_str}\n📝 کار: {task}" if user_lang == 'fa' else f"✅ Reminder set!\n⏰ Time: {time_str}\n📝 Task: {task}"
            bot.reply_to(message, success_msg)

        except ValueError:
            bot.reply_to(message, "❌ ساعت نامعتبر است. (مثال: 14:30)" if user_lang == 'fa' else "❌ Invalid time. (Example: 14:30)")
    elif text == '/lang':
        send_welcome(message)

def send_reminder(chat_id, task, lang):
    if lang == 'fa':
        msg = f"🔔 یادآوری!\n\n⏰ زمانش رسید:\n📝 {task}"
    else:
        msg = f"🔔 Reminder!\n\n⏰ It's time:\n📝 {task}"
    bot.send_message(chat_id, msg, parse_mode='Markdown')

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()

print("ربات روشن شد...")
bot.polling()
