import os
import datetime
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from keyboards import main_menu

router = Router()

raw_admins = os.getenv("ADMIN_ID", "")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in raw_admins.split(",") if admin_id.strip()]
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID") 
POST_CHANNEL_ID = os.getenv("POST_CHANNEL_ID") 

class ChannelPostState(StatesGroup):
    waiting_for_content = State()
    confirming = State()

@router.message(Command("post_chanel"))
async def channel_post_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(ChannelPostState.waiting_for_content)
    await message.answer(
        "📝 <b>Telegram kanalga post joylash uchun post xabarini yuboring:</b>\n\n"
        "<i>(Xabar matn, rasm yoki video bo'lishi mumkin)</i>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.message(ChannelPostState.waiting_for_content)
async def process_channel_post_content(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Amaliyot bekor qilindi.", reply_markup=main_menu())
        return

    original_text = message.caption or message.text or ""
    await state.update_data(
        c_msg_id=message.message_id,
        c_chat_id=message.chat.id,
        c_text=original_text,
        c_is_media=bool(message.photo or message.video)
    )

    confirm_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="chanel_confirm")],
        [types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="chanel_cancel")]
    ])

    await message.answer("Kanalga yuboriladigan post quyidagicha ko'rinadi. Tasdiqlaysizmi?")
    await message.copy_to(chat_id=message.chat.id, reply_markup=confirm_kb)
    await state.set_state(ChannelPostState.confirming)

@router.callback_query(ChannelPostState.confirming, F.data == "chanel_cancel")
async def cancel_channel_post(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try: await callback.message.delete()
    except: pass
    await callback.message.answer("❌ Post yuborish bekor qilindi.", reply_markup=main_menu())

@router.callback_query(ChannelPostState.confirming, F.data == "chanel_confirm")
async def confirm_channel_post(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    c_msg_id = data.get('c_msg_id')
    c_chat_id = data.get('c_chat_id')
    c_text = data.get('c_text', "")
    c_is_media = data.get('c_is_media', False)
    admin_name = callback.from_user.full_name
    admin_username = f"@{callback.from_user.username}" if callback.from_user.username else "Mavjud emas"

    try:
        await bot.copy_message(
            chat_id=REQUIRED_CHANNEL_ID,
            from_chat_id=c_chat_id,
            message_id=c_msg_id
        )

        report_text = (
            f"{c_text}\n\n"
            "----------------------------------------\n"
            f"👤 <b>Admin:</b> {admin_name}\n"
            f"👤 <b>Admin Username:</b> {admin_username}\n"
            f"📢 <b>Kanal:</b> {REQUIRED_CHANNEL_ID}\n"
            f"📅 <b>Vaqt:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if c_is_media:
            await bot.copy_message(
                chat_id=POST_CHANNEL_ID,
                from_chat_id=c_chat_id,
                message_id=c_msg_id,
                caption=report_text,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=POST_CHANNEL_ID,
                text=report_text,
                parse_mode="HTML"
            )

        try: await callback.message.delete()
        except: pass
        await callback.message.answer("✅ Post muvaffaqiyatli kanalga joylandi!", reply_markup=main_menu())

    except Exception as e:
        await callback.message.answer(f"❌ Xatolik yuz berdi: {e}")
    
    await state.clear()