import os
import asyncio
import datetime
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from keyboards import main_menu
from db.database import get_all_users, get_users_with_phone, get_users_without_phone

router = Router()

# Admin ID va Kanal sozlamalari
raw_admins = os.getenv("ADMIN_ID", "")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in raw_admins.split(",") if admin_id.strip()]
POST_CHANNEL_ID = os.getenv("POST_CHANNEL_ID")

class PostState(StatesGroup):
    selecting_type = State()
    waiting_for_post = State()
    confirming_post = State()

@router.message(Command("post"))
async def post_command_handler(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🚀 Start bosganlar")],
        [types.KeyboardButton(text="📞 Telefon raqami mavjudlar")],
        [types.KeyboardButton(text="👥 Barcha foydalanuvchilar")],
        [types.KeyboardButton(text="❌ Bekor qilish")]
    ], resize_keyboard=True)

    await state.set_state(PostState.selecting_type)
    await message.answer("👥 <b>Post yuborish uchun foydalanuvchi turini tanlang:</b>", reply_markup=kb, parse_mode="HTML")

@router.message(PostState.selecting_type, F.text.in_(["🚀 Start bosganlar", "📞 Telefon raqami mavjudlar", "👥 Barcha foydalanuvchilar"]))
async def select_type_handler(message: types.Message, state: FSMContext):
    user_type = message.text
    if user_type == "🚀 Start bosganlar":
        users = get_users_without_phone()
    elif user_type == "📞 Telefon raqami mavjudlar":
        users = get_users_with_phone()
    else:
        users = get_all_users()

    await state.update_data(target_users=users, user_type_name=user_type)
    await state.set_state(PostState.waiting_for_post)
    
    cancel_kb = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)
    await message.answer(
        f"✅ <b>{user_type}</b> tanlandi.\n👤 Soni: <b>{len(users)}</b> ta.\n\n📝 Endi postni yuboring:",
        reply_markup=cancel_kb,
        parse_mode="HTML"
    )

@router.message(PostState.waiting_for_post)
async def waiting_post_handler(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Post yuborish bekor qilindi.", reply_markup=main_menu())
        return

    original_text = message.caption or message.text or ""
    
    await state.update_data(
        p_msg_id=message.message_id, 
        p_chat_id=message.chat.id,
        p_text=original_text,
        is_media=bool(message.photo or message.video)
    )

    confirm_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_send")],
        [types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_send")]
    ])

    await message.answer("Siz yuborgan post quyidagicha ko'rinadi. Tasdiqlaysizmi?")
    await message.copy_to(chat_id=message.chat.id, reply_markup=confirm_kb)
    await state.set_state(PostState.confirming_post)

@router.callback_query(PostState.confirming_post, F.data == "cancel_send")
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try: await callback.message.delete()
    except: pass
    await callback.message.answer("❌ Sizning postingiz bekor qilindi.", reply_markup=main_menu())

@router.callback_query(PostState.confirming_post, F.data == "confirm_send")
async def confirm_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    users = data.get('target_users', [])
    user_type_name = data.get('user_type_name', "Noma'lum")
    p_msg_id = data.get('p_msg_id')
    p_chat_id = data.get('p_chat_id')
    p_text = data.get('p_text', "")
    is_media = data.get('is_media', False)
    admin_name = callback.from_user.full_name

    if not p_msg_id or not p_chat_id:
        await callback.answer("❌ Xatolik: Post ma'lumotlari topilmadi!", show_alert=True)
        return

    try: await callback.message.delete()
    except: pass
    
    status_msg = await bot.send_message(chat_id=callback.from_user.id, text="🚀 Post yuborish boshlandi...")
    
    success_count = 0
    fail_count = 0

    for user in users:
        try:
            await bot.copy_message(chat_id=user[0], from_chat_id=p_chat_id, message_id=p_msg_id)
            success_count += 1
            await asyncio.sleep(0.05)
        except:
            fail_count += 1

    full_report = (
        f"{p_text}\n\n"
        "----------------------------------------\n"
        "📢 <b>Yangi post yuborildi!</b>\n\n"
        f"<b>👤 Admin:</b> {admin_name}\n"
        f"<b>👥 Kimlarga:</b> {user_type_name}\n"
        f"<b>✅ Muvaffaqiyatli:</b> {success_count}\n"
        f"<b>❌ Xatolik:</b> {fail_count}\n"
        f"<b>📊 Jami:</b> {len(users)}\n"
        f"<b>📅 Vaqt:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        if is_media:
            await bot.copy_message(
                chat_id=POST_CHANNEL_ID,
                from_chat_id=p_chat_id,
                message_id=p_msg_id,
                caption=full_report,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=POST_CHANNEL_ID,
                text=full_report,
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Kanal hisobotida xato: {e}")

    await bot.send_message(
        chat_id=callback.from_user.id,
        text=f"✅ Post yuborish yakunlandi!\n\n<b>{success_count}</b> ta xabar yuborildi.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )
    await state.clear()

@router.message(PostState.selecting_type, F.text == "❌ Bekor qilish")
@router.message(PostState.waiting_for_post, F.text == "❌ Bekor qilish")
async def process_cancel_all(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ <b>Post yuborish bekor qilindi.</b>\n\n🏠 Bosh sahifaga qaytdingiz.", 
        reply_markup=main_menu(), 
        parse_mode="HTML"
    )