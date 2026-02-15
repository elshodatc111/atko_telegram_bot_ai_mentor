from aiogram import Router, types, F
from keyboards import main_menu, cours_about

router = Router()

@router.message(F.text == "📘 Kurslar")
async def courses_handler(message: types.Message):
    await message.answer(
        "🇰🇷 <b>Koreys tili kurslari</b>\n\n"
        "Bizda Koreys tilini <b>noldan boshlab</b> o‘rganish uchun bepul va pullik kurslar mavjud 👇\n\n"
        "🆓 <b>Bepul kurslar:</b>\n"
        "• Hangil (koreys alifbosi)\n"
        "• To‘g‘ri talaffuz asoslari\n"
        "• Oddiy o‘qish va tushunish\n\n"
        "🔒 <b>Pullik kurslar:</b>\n"
        "• To‘liq video darslar\n"
        "• Grammatik tushuntirishlar\n"
        "• Amaliy mashqlar va testlar\n"
        "• Natijaga yo‘naltirilgan ta’lim\n\n"
        "⬇️ Quyidagi bo‘limlardan birini tanlang:",
        reply_markup=cours_about(),
        parse_mode="HTML"
    )

@router.message(F.text == "🔒 Koreys tili pullik kurslar")
async def pro_courses_handler(message: types.Message):
    await message.answer(
        "🔒 <b>Pullik video kurslar</b>\n\n"
        "Hozirgi vaqtda <b>Koreys tili</b> va <b>Nemis tili</b> bo‘yicha "
        "<b>pullik video kurslar</b> professional tarzda tayyorlanmoqda. 🎬\n\n"

        "📚 <b>Rejalashtirilgan kurslar:</b>\n"
        "🇰🇷 Koreys tili — to‘liq video darslar, grammatika va amaliy mashqlar\n"
        "🇩🇪 Nemis tili — noldan boshlab bosqichma-bosqich o‘rganish\n\n"

        "✨ Ushbu kurslar:\n"
        "• Tajribali ustozlar tomonidan tayyorlanadi\n"
        "• Amaliy va tushunarli metodika asosida bo‘ladi\n"
        "• Natijaga yo‘naltirilgan ta’limni ta’minlaydi\n\n"

        "⏳ Kurslar yakunlangach, bu yerda e’lon qilinadi.\n"
        "Iltimos, yangiliklarni kuzatib boring!",
        reply_markup=cours_about(),
        parse_mode="HTML"
    )


@router.message(F.text == "⬅️ Orqaga")
async def back_handler(message: types.Message):
    await message.answer("Bosh menyuga qaytish:", reply_markup=main_menu())



