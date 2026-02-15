import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from handlers import get_handlers_router

# .env faylini yuklash
load_dotenv()

async def main():
    # 1. Loglarni sozlash (Xatoliklarni terminalda aniq ko'rish uchun)
    logging.basicConfig(level=logging.INFO)

    # 2. Tarmoq ulanishini sozlash (ServerDisconnectedError oldini olish uchun)
    # Ulanish kutish vaqtini 40 soniya qilib belgilaymiz
    session = AiohttpSession()
    
    # 3. Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=os.getenv("BOT_TOKEN"), 
        session=session
    )
    dp = Dispatcher()

    # 4. Routerlarni ulash
    dp.include_router(get_handlers_router())

    print("Bot ishga tushdi...")
    
    try:
        # Eski kelib qolgan xabarlarni (updates) tozalash
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Botni ishga tushirish
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logging.error(f"Polling jarayonida xatolik: {e}")
    finally:
        # Seansni yopish
        await bot.session.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot to'xtatildi!")
        try:
            loop = asyncio.get_event_loop()
            tasks = asyncio.all_tasks(loop)
            for task in tasks:
                task.cancel()
        except:
            pass