from aiogram import Router, types, F
from keyboards import main_menu

router = Router()

@router.message(F.text == "🏫 ATKO haqida")
async def info_handler(message: types.Message):
    await message.delete()
    await message.answer(
        "🎓 <b>ATKO O‘quv Markazi</b>\n\n"
        "ATKO — xorijda <b>o‘qish</b> va <b>ishlash</b>ni maqsad qilganlar uchun\n"
        "til bilimlarini mustahkamlashga ixtisoslashgan zamonaviy o‘quv markazi.\n\n"
        "📌 <b>Bizning asosiy yo‘nalishlarimiz:</b>\n"
        "🇩🇪 <b>Nemis tili</b> — ish va ta’lim uchun\n"
        "🇰🇷 <b>Koreys tili</b> — ish va ta’lim uchun\n\n"
        "📚 Ta’lim jarayoni boshlang‘ich darajadan boshlab,\n"
        "bosqichma-bosqich aniq natijagacha olib boriladi.\n\n"
        "👨‍🏫 Tajribali ustozlar, tizimli darslar va qulay muhit.\n"
        "🎯 Har bir o‘quvchi uchun individual yondashuv.\n\n"
        "🌐 <b>Ijtimoiy tarmoqlarimiz:</b>\n"
        "📢 Telegram kanal: <a href=\"https://t.me/atko_teams\">@atko_teams</a>\n"
        "📸 Instagram sahifa: <a href=\"https://instagram.com/atko_teams\">@atko_teams</a>\n"
        "▶️ YouTube kanal: <a href=\"https://youtube.com/@atko_teams\">@atko_teams</a>\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_menu(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )