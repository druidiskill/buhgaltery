from aiogram import Router, F
from aiogram.filters import Command

from aiogram.types import Message, MessageEntity
from tg_main import bot, admins, teachers
from db import get_students_by_tg_ids, update_hi_mess, get_all_students, db_take_injection

other_router = Router()


@other_router.message(Command("start"))
async def test_start(message:Message):
    print(message.text)



@other_router.message(F.text.startswith("injection\n"))
async def take_injection(message:Message):
    if message.from_user.id in admins:
        data = message.text[10:]
        result = await db_take_injection(data=data)
        if len(str(result)) > 4096:
            for x in range(0, len(str(result)), 4096):
                await message.answer(str(result)[x:x + 4096])
        else:
            await message.answer(str(result))


@other_router.message(F.text.startswith("send_all"))
async def send_all(message:Message):
    data_fin = message.text.find("\n")
    data = message.text[:data_fin].split("_")[2:]
    if message.chat.id in admins:
        if data[0] == "admins":
            for admin in admins:
                await bot.send_message(chat_id=admin, text=message.text[data_fin:])
        if data[0] == "teachers":
            for teacher in teachers.values():
                await bot.send_message(chat_id=teacher, text=message.text[data_fin:])
        if data[0] == "students":
            students = await get_all_students(column="tg_id")
            for student in set(students):
                if student[0] != "":
                    try:
                        await bot.send_message(chat_id=student[0], text=message.text[data_fin:])
                    except:
                        pass




async def send_hi_mess(tg_id:int):
    stud_info = await get_students_by_tg_ids(tg_id=tg_id, column="Par_name")
    hi_text = f"Здравствуйте, {stud_info[0][0]}!\nРады приветствовать Вас в нашем боте.\nНадеемся, что он упростит Ваше сотрудничество с нами.\nФункционал будет постоянно развиваться. Ваше мнение для нас очень важно!\nВсе предложения и замечания просим присылать личными сообщениями.\nhttps://t.me/dru_i_d\nЧтоб начать пользоваться перейдите в 'Меню' и выберите 'Режим Учащегося'"
    await bot.send_message(chat_id=tg_id, text=hi_text)
    await update_hi_mess(tg_id=tg_id)