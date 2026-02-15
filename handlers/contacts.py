from aiogram import Router, types, F
from keyboards import main_menu # Importni unutmaymiz

router = Router()

@router.message(F.text == "📍 Manzil")
async def location_handler(message: types.Message):
    try:
        await message.delete()
    except:
        pass
    text = (
        "📍 <b>ATKO O‘quv Markazi manzili</b>\n\n"
        "🏙 <b>Qarshi shahri</b>\n"
        "🏠 Mustaqillik shox ko‘chasi, 2-uy\n"
        "📌 Mo‘ljal: <b>Viloyat hokimligi ro‘parasida</b>\n\n"
        "Agar manzilni topishda qiyinchilik bo‘lsa,\n"
        "☎️ <b>Aloqa</b> bo‘limi orqali murojaat qiling."
    )    
    await message.answer(
        text=text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )
    await message.answer_location(
        latitude=38.83819288235711,
        longitude=65.79336671058141
    )

@router.message(F.text == "☎️ Aloqa")
async def contact_handler(message: types.Message):
    try:
        await message.delete()
    except:
        pass

    contact_text = (
        "📞 <b>ATKO O‘quv Markazi bilan bog‘lanish</b>\n\n"
        "☎️ <b>Telefon:</b> +998 91 950 1101\n"
        "💬 <b>Telegram:</b> @atko_teams\n\n"
        "⏰ <b>Ish vaqti:</b> 09:00 – 18:00"
    )
    
    await message.answer(
        text=contact_text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )