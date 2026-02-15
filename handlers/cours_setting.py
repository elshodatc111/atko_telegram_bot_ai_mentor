from aiogram import Router, types, F
from keyboards import main_menu, cours_setting

router = Router()
@router.message(F.text == "/setting")
async def courses_settings(message: types.Message):
    await message.answer("Kerakli bo'limni tanlang:", reply_markup=cours_setting())

@router.message(F.text == "/orqaga")
async def back_settings(message: types.Message):
    await message.answer("Bosh menyuga qaytish:", reply_markup=main_menu())
