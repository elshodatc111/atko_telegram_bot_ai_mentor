from aiogram import Router, types, F, Bot
import os
from keyboards import free_cours_about, main_menu, phone_keyboard2
from db.database import get_setting, get_user_phone, update_user_phone
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Kurslar bo'limi uchun maxsus holat
class CourseState(StatesGroup):
    waiting_for_phone = State()

router = Router()

# .env fayldan ma'lumotlarni yuklaymiz
CHANNEL_ID = os.getenv("BEPUL_KURS_CHANNEL_ID")
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID")

@router.message(F.text == "🆓 Koreys tili bepul kurslar")
async def courses_handler(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    
    # 1. Telefon raqamini tekshirish
    phone = get_user_phone(user_id)
    if not phone:
        # MUHIM: Kurslar uchun raqam so'rash holatiga o'tkazamiz
        await state.set_state(CourseState.waiting_for_phone)
        await message.answer(
            "⚠️ <b>Darslarni ko'rish uchun ro'yxatdan o'tish lozim!</b>\n\n"
            "🤖 <b>ATKO AI tizimi</b> darslardan foydalanish uchun\n"
            "telefon raqamingizni tasdiqlashingizni so'raydi.\n\n"
            "👇 Quyidagi tugma orqali raqamingizni yuboring:",
            reply_markup=phone_keyboard2(),
            parse_mode="HTML"
        )
        return 

    # 2. Kanalga a'zolikni tekshirish
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        if member.status in ["left", "kicked"]:
            subscribe_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{REQUIRED_CHANNEL_ID[1:]}")],
                [types.InlineKeyboardButton(text="✔️ Tekshirish.", callback_data="check_sub_courses")]
            ])
            
            await message.answer(
                "⚠️ <b>Uzr, darslarni ko‘rishni davom ettirish uchun kanalimizga a’zo bo‘lishingiz shart.</b>\nKanalga a’zo bo‘lib, so‘ng <b>“Tekshirish”</b> tugmasini bosing.",
                reply_markup=subscribe_kb,
                parse_mode="HTML"
            )
            return
    except Exception as e:
        print(f"Obuna tekshirishda xato: {e}")

    # 3. Barcha shartlar bajarilgan bo'lsa, darslar menyusi chiqadi
    await message.answer(
        "🇰🇷 <b>Bepul Hangil kursi</b>\n\n"
        "Ushbu bepul kurs orqali siz <b>Koreys alifbosi — Hangil</b>ni "
        "<b>noldan boshlab</b> o‘rganasiz.\n\n"
        "🎥 <b>Kurs tarkibi (10 ta video dars):</b>\n"
        "1️⃣ <b>Kirish qismi</b> — Hangil nima va qanday o‘rganiladi\n"
        "2️⃣ Unlilar (Vowels)\n"
        "3️⃣ Undoshlar (Consonants)\n"
        "4️⃣ Ikki harfli tovushlar\n"
        "5️⃣ Harflarni birlashtirish\n"
        "6️⃣ Bo‘g‘inlar va o‘qish qoidalari\n"
        "7️⃣ To‘g‘ri talaffuz mashqlari\n"
        "8️⃣ O‘qish tezligini oshirish\n"
        "9️⃣ Amaliy misollar bilan o‘qish\n"
        "🔟 Yakuniy mustahkamlash darsi\n\n"
        "✅ <b>Kurs bepul</b> va barcha foydalanuvchilar uchun ochiq.\n"
        "📌 Kursni tugatgach, siz koreyscha so‘zlarni o‘qiy olasiz.\n\n"
        "⬇️ Quyidagi bo‘limlardan birini tanlang:",
        reply_markup=free_cours_about(),
        parse_mode="HTML"
    )

# --- FAQAT KURSLAR BO'LIMI UCHUN KONTAKT QABUL QILISH ---
# MUHIM: Bu xendler MentorState ga aralashmasligi uchun CourseState da bo'lishi shart!
@router.message(CourseState.waiting_for_phone, F.contact)
async def course_contact_handler(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    
    # Raqamni bazada yangilash
    update_user_phone(user_id, phone)
    
    # Holatni tozalaymiz
    await state.clear()
    
    # Xabarni o'chirib, darslar menyusini chaqiramiz
    await message.answer("✅ Raqamingiz muvaffaqiyatli saqlandi!")
    await courses_handler(message, bot, state)

# --- KURSLAR UCHUN CALLBACK QUERY HANDLER ---
@router.callback_query(F.data == "check_sub_courses")
async def check_subscription_callback(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        
        if member.status not in ["left", "kicked"]:
            await callback.answer("✅ Rahmat! Obuna tasdiqlandi.", show_alert=True)
            await callback.message.delete()
            await courses_handler(callback.message, bot, state)
        else:
            await callback.answer("❌ Siz hali kanalga a’zo emassiz.\nIltimos, davom etish uchun kanalga qo‘shiling.", show_alert=True)
    except Exception as e:
        await callback.answer("Xatolik yuz berdi.")

# --- VIDEOLARNI YUBORISH ---
@router.message(F.text.contains("-dars") | (F.text == "🎬 Kirish darsi") | (F.text == "📘 Darslik (PDF)"))
async def send_lesson_video(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    
    # Xavfsizlik uchun yana bir bor telefonni tekshiramiz
    if not get_user_phone(user_id):
        await message.answer("📲 Iltimos, video darslarni ko‘rishdan oldin ro‘yxatdan o‘ting.\nBuning uchun telefon raqamingizni yuboring.", reply_markup=main_menu())
        return
    
    lesson_name = message.text
    msg_id = get_setting(lesson_name)
    
    if msg_id:
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=CHANNEL_ID,
                message_id=int(msg_id),
                caption=f"🎓 Ushbu video kurs ATKO o‘quv markazi asoschisi\nSuvonob Abbos tomonidan ishlab chiqilgan bo‘lib, \namaliy va samarali metodika asosida tayyorlangan.",
                parse_mode="HTML",
                protect_content=True 
            )
        except Exception as e:
            await message.answer("❌ Kechirasiz, video yuborishda texnik xatolik yuz berdi.")
    else:
        await message.answer(f"⚠️ <b>{lesson_name}</b> videosi hali yuklanmagan.")