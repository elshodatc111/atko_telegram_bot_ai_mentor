import os
import datetime
from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from keyboards import main_menu
from db.database import add_user, set_setting, get_setting

router = Router()

# .env faylidan log kanal ID sini olish
START_LOG_CHANNEL = os.getenv("START_USER_CHANEL_ID")

@router.message(Command("start"))
async def start_handler(message: types.Message, bot: Bot):
    full_name = message.from_user.full_name
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_new_user = add_user(user_id, full_name, message.from_user.username)
    if is_new_user:
        report_text = (
            "<b>🆕 Yangi foydalanuvchi start bosdi!</b>\n\n"
            f"<b>👤 Ism:</b> {full_name}\n"
            f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
            f"<b>🔗 Username:</b> {username}\n"
            f"<b>📅 Vaqt:</b> {now}"
        )
        try:
            await bot.send_message(
                chat_id=START_LOG_CHANNEL, 
                text=report_text, 
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Log xatosi: {e}")

    # 3. Foydalanuvchi yuborgan /start buyrug'ini o'chirish (Interfeys tozaligi uchun)
    try:
        await message.delete()
    except Exception as e:
        # Ba'zida xabarni o'chirib bo'lmasa (masalan, vaqt o'tib ketsa), bot to'xtab qolmasligi uchun
        print(f"Xabarni o'chirishda xato: {e}")

    # 4. Start rasmini bazadan olish
    photo_id = get_setting("welcome_photo")
    
    welcome_caption = (
        f"🎓 <b>ATKO O‘quv Markazi</b> rasmiy Telegram botiga xush kelibsiz.\n\n"
        "<b>ATKO</b> — xorijda <b>o‘qish</b> va <b>ishlash</b>ni maqsad qilganlar uchun\n"
        "🇩🇪 <b>Nemis</b> va 🇰🇷 <b>Koreys </b> tillariga ixtisoslashgan zamonaviy o‘quv markazidir.\n\n"
        "📚 Ta’lim boshlang‘ich darajadan aniq natijagacha olib boriladi.\n"
        "👨‍🏫 Tajribali ustozlar va tizimli darslar.\n\n"
        "Kerakli bo‘limni tanlang 👇"
    )

    if photo_id:
        try:
            await message.answer_photo(
                photo=photo_id,
                caption=welcome_caption,
                reply_markup=main_menu(),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Rasm yuborishda xato: {e}")
            await message.answer(
                f"Assalomu alaykum, <b>{full_name}</b>!\n\n" + welcome_caption, 
                reply_markup=main_menu(),
                parse_mode="HTML"
            )
    else:
        # Agar bazada rasm bo'lmasa oddiy matn
        await message.answer(
            f"Assalomu alaykum, <b>{full_name}</b>!\n\n" + welcome_caption,
            reply_markup=main_menu(),
            parse_mode="HTML"
        )

# 5. Kanal xabarlarini kuzatish (Hashtag orqali rasmni yangilash)
@router.channel_post(F.photo & F.caption.contains("#STARTIMAGE"))
async def update_start_image(message: types.Message):
    # Kanaldagi yangi rasm ID-sini bazaga saqlash
    new_photo_id = message.photo[-1].file_id
    set_setting("welcome_photo", new_photo_id)
    print(f"✅ Start rasmi BAZADA yangilandi! ID: {new_photo_id}")