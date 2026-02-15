from aiogram import Router, types, F
from keyboards import cours_setting

router = Router()

@router.message(F.text == "/chart")
async def courses_handler(message: types.Message):
    await message.answer("Bu yerda statistika:", reply_markup=cours_setting())

