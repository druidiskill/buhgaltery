import asyncio
from tg_main import bot, dp
from handlers.admin import admin_router
from handlers.teachers import teachers_router
from handlers.students import students_router
from handlers.other import other_router

async def main():
    dp.include_routers(other_router, admin_router, students_router, teachers_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())