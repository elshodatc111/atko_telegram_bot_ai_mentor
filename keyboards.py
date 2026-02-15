from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = [
        [KeyboardButton(text="🏫 ATKO haqida"), KeyboardButton(text="📘 Kurslar")],
        [KeyboardButton(text="📍 Manzil"), KeyboardButton(text="☎️ Aloqa")],
        [KeyboardButton(text="🤖 AI Mentor")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def phone_keyboard2():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def chat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Chatni yakunlash")]],
        resize_keyboard=True
    )

def cours_setting():
    kb = [
        [KeyboardButton(text="/post"), KeyboardButton(text="/post_chanel")],
        [KeyboardButton(text="/orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cours_about():
    kb = [
        [KeyboardButton(text="🆓 Koreys tili bepul kurslar")],
        [KeyboardButton(text="🔒 Koreys tili pullik kurslar")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def free_cours_about():
    kb = [
        [KeyboardButton(text="🎬 Kirish darsi"),KeyboardButton(text="1️⃣ 1-dars")],
        [KeyboardButton(text="2️⃣ 2-dars"),KeyboardButton(text="3️⃣ 3-dars")],
        [KeyboardButton(text="4️⃣ 4-dars"),KeyboardButton(text="5️⃣ 5-dars")],
        [KeyboardButton(text="6️⃣ 6-dars"),KeyboardButton(text="7️⃣ 7-dars")],
        [KeyboardButton(text="8️⃣ 8-dars"),KeyboardButton(text="9️⃣ 9-dars")],
        [KeyboardButton(text="📘 Darslik (PDF)"),KeyboardButton(text="⬅️ Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)