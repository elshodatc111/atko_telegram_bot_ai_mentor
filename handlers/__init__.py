from aiogram import Router
from .start import router as start_router
from .about import router as about_router
from .courses import router as courses_router
from .contacts import router as contacts_router
from .mentor import router as mentor_router
from .post import router as post_router
from .post_chanel import router as post_chanel_router
from .chart import router as statustika_router
from .cours_setting import router as cours_setting_router
from .cours_free import router as cours_free_router
from db.schema import create_tables

# Bot ishga tushayotganida jadvallarni yaratib olamiz
create_tables()

def get_handlers_router() -> Router:
    main_router = Router()
    main_router.include_routers(
        start_router,
        about_router,
        courses_router,
        contacts_router,
        cours_free_router,
        mentor_router,
        post_router,
        post_chanel_router,
        statustika_router,
        cours_setting_router
    )
    return main_router