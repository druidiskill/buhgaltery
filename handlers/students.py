from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from db import get_students_by_tg_ids, get_student_by_id, get_lessons_by_stud_id, get_teacher_by_id, get_lesson_by_IDS, \
    get_all_teachers
from tg_main import bot, teachers, admins

students_router = Router()

@students_router.callback_query(F.data.startswith('student_'))
async def student_info(callback:[CallbackQuery, str]):
    print("Информация об ученике")
    if type(callback) == CallbackQuery: # Несколько учеников
        await callback.message.delete()
        stud_id = callback.data.split("_")
    elif type(callback) == str: # 1 ученик
        stud_id = callback.split("_")
    stud_info = await get_student_by_id(id_stud=int(stud_id[1]))
    kb_list = []
    if '' in stud_info[:-2]:
        kb_list.append([InlineKeyboardButton(text="Дополнить данные", callback_data=f"studen_{stud_id[1]}")])
    lessons = await get_lessons_by_stud_id(id_stud=int(stud_id[1]))
    for lesson in lessons:
        lesson_name = await get_teacher_by_id(id_teach=int(lesson[1]))
        kb_list.append([InlineKeyboardButton(text=lesson_name[2], callback_data=f"stude_{stud_id[1]}_{lesson[1]}")])
    kb_list.append([InlineKeyboardButton(text="ИНФОРМАЦИЯ О СТУДИИ", callback_data=f"info_about_studio")])
    if type(callback) == CallbackQuery:
        if len(await get_students_by_tg_ids(tg_id=callback.message.from_user.id)) > 1:
            kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"root_student")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    text = f"{stud_info[1]} {stud_info[2]}"
    await bot.send_message(chat_id=stud_info[6], text=text, reply_markup=kb)



@students_router.message(Command("student"))
async def start_student(message: Message):
    print(message.chat.id, "Стартовая команда")
    await message.delete()
    ids = await get_students_by_tg_ids(tg_id=int(message.chat.id))
    if len(ids) != 0:
        if len(ids) > 1:
            kb_list = []
            for stud in ids:
                info_stud = await get_student_by_id(id_stud=int(stud[0]))
                kb_list.append([InlineKeyboardButton(text=f"{info_stud[1]} {info_stud[2]}", callback_data=f"student_{stud[0]}_{message.from_user.id}")])
            kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
            await message.answer("Выберите учащегося:", reply_markup=kb)
        else:
            await student_info(callback=f"student_{ids[0][0]}_{message.from_user.id}")


@students_router.message(Command("start"))
async def start_student_by_start(message: Message):
    tg_id = message.chat.id
    if tg_id not in admins:
        if tg_id not in teachers.values():
            await start_student(message=message)


@students_router.callback_query(F.data == "root_student")
async def student_start_call(callback:CallbackQuery):
    await start_student(message=callback.message)



@students_router.callback_query(F.data.startswith("studen_"))
async def change_student_info(callback:CallbackQuery):
    print(callback.message.chat.id, "Добавить информацию")
    await callback.message.delete()
    data = callback.data.split("_")[1:]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"student_{data[0]}")]])
    await callback.message.answer("Данная функция в стадии разработки", reply_markup=kb)



@students_router.callback_query(F.data.startswith("stude_"))
async def info_about_lessons(callback:CallbackQuery):
    print(callback.message.chat.id, "Информация о занятии")
    await callback.message.delete()
    data = callback.data.split("_")[1:]
    info_about_teacher = await get_teacher_by_id(id_teach=int(data[1]))
    lesson = await get_lesson_by_IDS(id_teach=int(data[1]), id_stud=int(data[0]))
    past_lessons = lesson[3].split(",")
    if past_lessons != ['']:
        last_lessons = lesson[2]-len(lesson[3].split(","))
    else:
        last_lessons = 0
    text = f"{info_about_teacher[1]}\n{info_about_teacher[2]}\n"
    text += "_______________\n"
    if last_lessons < 0:
        text += f"Неоплачено: {last_lessons * (-1)}"
    elif last_lessons > 0:
        text += f"Оплачено: {last_lessons}"
    else:
        text += f"Уроки закончились!!!"
    if info_about_teacher[1] in teachers.keys():
        url = f"tg://openmessage?user_id={teachers[info_about_teacher[1]]}"
    else:
        url = f"tg://openmessage?user_id=1087504926"
    kb_list = [[InlineKeyboardButton(text="Связаться с педагогом", url=url)]]
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"student_{data[0]}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text=text, reply_markup=kb)



@students_router.callback_query(F.data == "info_about_studio")
async def info_about_studio(callback:CallbackQuery):
    print(callback.message.chat.id, "Информация о студии")
    await callback.message.delete()
    text = "Приглашаем на наши занятия:\n(Занятие / Цена 1 зан. в абон. / Пробного зан.)"
    lessons = await get_all_teachers(column="ID, lesson_name, abon_stud, prob_stud")
    kb_list = []
    names = []
    for lesson in set(lessons):
        if lesson[1] not in names:
            kb_list.append([InlineKeyboardButton(text=f"{lesson[1]} / {lesson[2]} / {lesson[3]}", callback_data=f"info_about_studio_{lesson[0]}")])
            names.append(lesson[1])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"root_student")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text=text, reply_markup=kb)
    await callback.message.answer(text="О разовых мероприятиях, всю информацию можно получить в нашей группе:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ПЕРЕЙТИ В VK", url="https://vk.com/vasilekvoice")]]))


@students_router.callback_query(F.data.startswith("info_about_studio_"))
async def info_about_studio_lesson(callback:CallbackQuery):
    print(callback.message.chat.id, "Информация о уроках в студии")
    await callback.message.delete()
    lesson_id = callback.data.split("_")[3]
    lesson_info = await get_teacher_by_id(id_teach=int(lesson_id))
    text = f"{lesson_info[2]}\n\nАбонемент на 4 занятия: {lesson_info[3]*4}руб. ({lesson_info[3]}руб./занятие)\nПробное занятие: {lesson_info[5]}руб./занятие\n\nЖелаете уведомить руководителя о заинтересованности?"
    kb_list = [[InlineKeyboardButton(text="УВЕДОМИТЬ", callback_data=f"mess_vas_{lesson_id}")]]
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"info_about_studio")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text=text, reply_markup=kb)


@students_router.callback_query(F.data.startswith("mess_vas_"))
async def mess_vasil_about_interest(callback:CallbackQuery):
    print(callback.message.chat.id, "Уведомил в заинтересованности")
    await callback.message.delete()
    lesson_id = int(callback.data.split("_")[2])
    parent_id = int(callback.message.chat.id)
    lesson_info = await get_teacher_by_id(id_teach=lesson_id)
    student_info = await get_students_by_tg_ids(tg_id=parent_id, column="Par_name, tel")
    text = f"!!!!!!!!!!!!\n{student_info[0][0]}\n{student_info[0][1]}\n\n{lesson_info[2]}"
    await bot.send_message(chat_id=1087504926, text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Связаться в TG",
                                                                                                                                   url=f"tg://openmessage?user_id={parent_id}")]]))
    await callback.message.answer(text="В ближайшее время руководитель свяжется с Вами и ответит на все интересующие Вас вопросы",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Главное меню", callback_data="root_student")]]))