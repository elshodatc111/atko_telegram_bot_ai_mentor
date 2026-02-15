import os
import datetime
from groq import Groq
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import main_menu, phone_keyboard, chat_keyboard
from db.database import get_user_phone, update_user_phone

router = Router()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile" 

# .env fayldan kerakli kanal ID sini olish
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID") 
LEAVE_LOG_CHANNEL = os.getenv("LEAVE_USER_CHANEL_ID")

# --- SYSTEM PROMPT YANGILANDI ---
SYSTEM_PROMPT = """
Siz ATKO o'quv markazining professional AI mentorisiz. 
Sizning mutaxassisligingiz FAQAT Nemis tili va Koreys tilini o'rgatish hamda ATKO o'quv markazi haqida ma'lumot berishdir.

MUHIM QOIDA:
Koreys yoki nemis tili bo'yicha so'z so'ralsa, ALBATTA quyidagi tartibda javob bering:
1. So'zning o'sha tildagi yozilishi (masalan, Koreyscha bo'lsa Hangul alifbosida: 안녕하세요).
2. Qavs ichida o'qilishi (transkripsiyasi).
3. O'zbekcha ma'nosi.

Misol: "Koreys tilida salom qanday bo'ladi?" deb so'ralsa, "Koreys tilida salom 안녕하세요 (annyeonghaseyo) deb yoziladi" deb javob bering.

Qoidalar:
1. Faqat Nemis va Koreys tillari (grammatika, so'zlashuv, darslar) va ATKO markazi haqida javob bering.
2. Ishga joylashish, viza yoki boshqa o'quv markazidan tashqari begona mavzular haqida so'rashsa, muloyimlik bilan rad eting.
3. Foydalanuvchiga til o'rganishda motivatsiya bering va savollariga qisqa, aniq javob qaytaring.
4. Javoblar faqat matn ko'rinishida va o'zbek tilida bo'lsin.

ATKO o'quv markazi haqida ma'lumotlar:
- Manzil: Qarshi shahri, Mustaqillik ko'chasi, 2-uy.
- Mo'ljal: Viloyat hokimligi ro'parasi.
- Telefon: +998919501101
- Telegram admin: @atko001
- Ijtimoiy tarmoqlar (Telegram, Instagram, YouTube): @atko_teams
"""

class MentorState(StatesGroup):
    chatting = State()

# --- Yordamchi funksiya: Kanalga obunani tekshirish ---
async def check_subscription(bot: Bot, user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"Obunani tekshirishda xato: {e}")
    return False

# --- AI Mentor tugmasi bosilganda ---
@router.message(F.text == "🤖 AI Mentor")
async def mentor_handler(message: types.Message, bot: Bot, state: FSMContext):
    try: await message.delete()
    except: pass
        
    user_id = message.from_user.id
    phone = get_user_phone(user_id)

    if not phone:
        await message.answer(
            "📱 <b>Telefon raqamingizni yuboring</b>\n\n"
            "🤖 <b>AI Mentor</b> bilan muloqotni boshlash uchun\n"
            "telefon raqamingizni tasdiqlashingiz kerak.\n\n"
            "🔒 Raqamingiz faqat tizim xavfsizligi va\n"
            "muloqotni yaxshilash uchun ishlatiladi.\n\n"
            "👇 Quyidagi tugma orqali raqamingizni yuboring:",
            reply_markup=phone_keyboard(),
            parse_mode="HTML"
        )
        return

    is_subscribed = await check_subscription(bot, user_id)
    if not is_subscribed:
        subscribe_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{REQUIRED_CHANNEL_ID[1:]}")],
            [types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
        ])
        await message.answer(
            "⚠️ <b>AI Mentor</b>dan foydalanish uchun avval bizning kanalimizga a'zo bo'lishingiz kerak:",
            reply_markup=subscribe_kb,
            parse_mode="HTML"
        )
        return

    await state.set_state(MentorState.chatting)
    await message.answer(
        "🤖 <b>AI Mentor (ATKO) tayyor!</b>\n\n"
        "Men sizga <b>Nemis</b> va <b>Koreys</b> tillarini o'rganishda yordam beraman hamda "
        "markazimiz haqidagi savollaringizga javob beraman.\n\n"
        "📚 <b>Sizga quyidagilarda yordam bera olaman:</b>\n"
        "• Nemis va Koreys tili grammatikasi\n"
        "• Yangi so'zlar va talaffuz\n"
        "• O'quv markazimiz manzili va bog'lanish ma'lumotlari\n\n"
        "✍️ <b>Suhbatni boshlash uchun savolingizni yozing:</b>",
        reply_markup=chat_keyboard(),
        parse_mode="HTML"
    )

# --- Obunani tekshirish uchun Callback ---
@router.callback_query(F.data == "check_sub")
async def check_callback_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    phone = get_user_phone(user_id)
    
    if await check_subscription(bot, user_id):
        await callback.answer("✅ Raxmat!")
        await callback.message.delete()
        
        if phone:
            await state.set_state(MentorState.chatting)
            await callback.message.answer(
                "🤖 <b>AI Mentor (ATKO) tayyor!</b>\n\n"
                "Men sizga <b>Nemis</b> va <b>Koreys</b> tillarini o'rganishda yordam beraman hamda "
                "markazimiz haqidagi savollaringizga javob beraman.\n\n"
                "📚 <b>Sizga quyidagilarda yordam bera olaman:</b>\n"
                "• Nemis va Koreys tili grammatikasi\n"
                "• Yangi so'zlar va talaffuz\n"
                "• O'quv markazimiz manzili va bog'lanish ma'lumotlari\n\n"
                "✍️ <b>Suhbatni boshlash uchun savolingizni yozing:</b>",
                reply_markup=chat_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                "📱 <b>Telefon raqamingizni yuboring</b>\n\n"
                "👇 Quyidagi tugma orqali raqamingizni yuboring:",
                reply_markup=phone_keyboard(),
                parse_mode="HTML"
            )
    else:
        await callback.answer("❌ Siz hali ham kanalga a'zo emassiz!", show_alert=True)

# --- AI BILAN CHAT JARAYONI (FAQAT MATN UCHUN) ---
@router.message(MentorState.chatting, F.text)
async def ai_chat_handler(message: types.Message, bot: Bot, state: FSMContext):
    is_subscribed = await check_subscription(bot, message.from_user.id)
    if not is_subscribed:
        await state.clear()
        subscribe_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{REQUIRED_CHANNEL_ID[1:]}")],
            [types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
        ])
        await message.answer(
            "⚠️ Uzr, AI Mentor bilan suhbatni davom ettirish uchun kanalimizga a'zo bo'lishingiz shart:",
            reply_markup=subscribe_kb,
            parse_mode="HTML"
        )
        return

    if message.text == "❌ Chatni yakunlash":
        try: await message.delete()
        except: pass
        await state.clear()
        await message.answer(
            "✅ <b>AI Mentor bilan suhbat yakunlandi.</b>\n\n🏠 Bosh sahifaga qaytdingiz.",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.3, # Aniqlikni oshirish uchun temperaturani tushirdik
        )
        
        response_text = completion.choices[0].message.content
        if response_text:
            # HTML formatlash orqali koreys harflarini aniqroq chiqaramiz
            await message.answer(response_text, parse_mode="HTML") 
    except Exception as e:
        print(f"Groq AI Xatosi: {e}")
        # Agar HTML xato bersa, oddiy matnda yuboramiz
        try:
            await message.answer(response_text, parse_mode=None)
        except:
            await message.answer("Tizimda vaqtinchalik uzilish bo'ldi. Birozdan so'ng urinib ko'ring.")

# --- MATN BO'LMAGAN XABARLAR UCHUN FILTR ---
@router.message(MentorState.chatting) 
async def ai_no_text_handler(message: types.Message):
    await message.answer(
        "⚠️ <b>AI Mentor faqat matnli xabarlarni qabul qiladi.</b>\n\n"
        "Iltimos, savolingizni matn ko'rinishida yozib yuboring. 😊",
        parse_mode="HTML"
    )

# --- Kontakt yuborilganda ---
@router.message(F.contact)
async def contact_handler(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    full_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    
    update_user_phone(user_id, phone) 

    report_text = (
        "<b>📱 Yangi kontakt (AI Mentor uchun) olindi!</b>\n\n"
        f"<b>👤 Ism:</b> {full_name}\n"
        f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
        f"<b>🔗 Username:</b> {username}\n"
        f"<b>📞 Tel:</b> {phone}\n"
        f"<b>📅 Vaqt:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )    
    try:
        await bot.send_message(chat_id=LEAVE_LOG_CHANNEL, text=report_text, parse_mode="HTML")
    except Exception as e:
        print(f"Log xato: {e}")

    if await check_subscription(bot, user_id):
        await state.set_state(MentorState.chatting)
        await message.answer(
            "✅ <b>Raqamingiz muvaffaqiyatli saqlandi!</b>\n\n"
            "🤖 <b>AI Mentor (ATKO) ishga tushdi.</b>\n"
            "Nemis yoki Koreys tili bo‘yicha savollaringizni yo‘llashingiz mumkin:",
            reply_markup=chat_keyboard(),
            parse_mode="HTML"
        )
    else:
        subscribe_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{REQUIRED_CHANNEL_ID[1:]}")],
            [types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
        ])
        await message.answer(
            "✅ Raqamingiz saqlandi! Endi AI Mentorni ishga tushirish uchun kanalimizga a'zo bo'lishingiz kerak:",
            reply_markup=subscribe_kb,
            parse_mode="HTML"
        )