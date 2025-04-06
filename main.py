from keep_alive import keep_alive
keep_alive()

import telebot
import json
import os
import time
import threading

TOKEN = '7274047594:AAHX0LZyPEidEGGL1KYbVOM7tjK3jQYBOIE'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 5459011640  # <<< O'Z TELEGRAM IDingiz

majburiy_kanallar = [
    "@kanal1",
    "@kanal2",
    "@kanal3",
    "@kanal4",
    "@kanal5"
]

kanal_links = {
    "@kanal1": "https://t.me/+dNO7mW9b6QMwNTVi",
    "@kanal2": "https://t.me/+APooVFJq7IllYWFi",
    "@kanal3": "https://t.me/+fVg5eyX5Sfo0NGFi",
    "@kanal4": "https://t.me/+1hCrEep284djYzgy",
    "@kanal5": "https://t.me/+q3hQxyUFM9AzOTRi"
}

ATTEMPT_FILE = "attempts.json"
KINO_FILE = "kinolar.json"
ADMIN_STATE = {}

def load_json_file(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def obuna_tekshir(user_id):
    for kanal in majburiy_kanallar:
        try:
            status = bot.get_chat_member(kanal, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def clear_attempts_daily():
    while True:
        time.sleep(86400)
        save_json_file(ATTEMPT_FILE, {})

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    attempts = load_json_file(ATTEMPT_FILE)
    attempts[str(user_id)] = 0
    save_json_file(ATTEMPT_FILE, attempts)

    if obuna_tekshir(user_id):
        bot.send_message(user_id, "Xush kelibsiz! Kino raqamini yuboring:")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        for i, kanal in enumerate(majburiy_kanallar, start=1):
            markup.add(telebot.types.InlineKeyboardButton(
                text=f"[{i}] - Kanal", url=kanal_links[kanal]
            ))
        markup.add(telebot.types.InlineKeyboardButton(
            text="✅ Tekshirish", callback_data="check_subs"
        ))
        bot.send_message(user_id, "Quyidagi kanallarga obuna bo‘ling va Tekshirish tugmasini bosing:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def tekshirish_callback(call):
    user_id = call.message.chat.id
    user_id_str = str(user_id)
    attempts = load_json_file(ATTEMPT_FILE)
    attempts[user_id_str] = attempts.get(user_id_str, 0) + 1
    save_json_file(ATTEMPT_FILE, attempts)

    if obuna_tekshir(user_id) or attempts[user_id_str] >= 2:
        bot.answer_callback_query(call.id, "✅ Tekshiruv muvaffaqiyatli!", show_alert=True)
        bot.send_message(user_id, "Endi kino raqamini yuboring.")
    else:
        bot.answer_callback_query(
            call.id,
            f"Siz hali barcha kanallarga obuna bo‘lmadingiz. Urinish: {attempts[user_id_str]}/2",
            show_alert=True
        )

@bot.message_handler(commands=['del'])
def delete_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "To‘g‘ri format: /del <raqam>")
        return
    raqam = parts[1]
    kinolar = load_json_file(KINO_FILE)
    if raqam in kinolar:
        del kinolar[raqam]
        save_json_file(KINO_FILE, kinolar)
        bot.reply_to(message, f"{raqam}-raqamli video o‘chirildi.")
    else:
        bot.reply_to(message, f"{raqam}-raqamli video topilmadi.")

@bot.message_handler(func=lambda message: message.text.isdigit())
def raqam_kiritildi(message):
    user_id = message.chat.id
    text = message.text

    if message.from_user.id == ADMIN_ID:
        ADMIN_STATE[user_id] = text
        bot.send_message(user_id, f"Endi {text}-raqamli videoni yuboring.")
    else:
        attempts = load_json_file(ATTEMPT_FILE)
        if not obuna_tekshir(user_id) and attempts.get(str(user_id), 0) < 2:
            bot.send_message(user_id, "Iltimos, avval barcha kanallarga obuna bo‘ling va /start buyrug‘ini bosing.")
            return

        kinolar = load_json_file(KINO_FILE)
        file_id = kinolar.get(text)
        if file_id:
            bot.send_video(user_id, file_id, caption=f"{text}-raqamli kino")
        else:
            bot.send_message(user_id, f"{text}-raqamli kino mavjud emas.")

@bot.message_handler(content_types=['video'])
def video_qabul(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return
    raqam = ADMIN_STATE.get(user_id)
    if not raqam:
        bot.send_message(user_id, "Avval raqam yuboring, keyin video.")
        return
    kinolar = load_json_file(KINO_FILE)
    kinolar[raqam] = message.video.file_id
    save_json_file(KINO_FILE, kinolar)
    bot.send_message(user_id, f"{raqam}-raqamli video saqlandi.")
    del ADMIN_STATE[user_id]

# Urinishlarni har 24 soatda tozalash
threading.Thread(target=clear_attempts_daily, daemon=True).start()

# Botni ishga tushirish
bot.polling()
