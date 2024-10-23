from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from db import print_results, get_teacher_info, get_students_ID_by_teacher_ID, get_student_by_id, get_lesson_by_IDS, \
    add_lesson, get_teacher_by_id, get_all_students
from handlers.other import send_hi_mess
from tg_main import teachers, bot
import datetime as dt

teachers_router = Router()

@teachers_router.message(Command("teacher"))
async def start_teacher(message: Message):
    need_mess = await get_all_students()
    for stud in need_mess:
        if stud[6] != '':
            if stud[8] == 0:
                try:
                    await send_hi_mess(tg_id=int(stud[6]))
                except:
                    pass
    if int(message.chat.id) in teachers.values():
        for key in teachers.keys():
            if teachers[key] == int(message.chat.id):
                teacher_name = key
        kb_list = [[InlineKeyboardButton(text="РЕЗУЛЬТАТЫ НЕДЕЛИ", callback_data=f"get_results_{message.chat.id}")]]
        lessons = await get_teacher_info(teach_name=teacher_name)
        for lesson in lessons:
            kb_list.append([InlineKeyboardButton(text=lesson[0], callback_data=f"teachers_less_{lesson[1]}")])
        kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
        await message.answer("Выберите предмет:", reply_markup=kb)


@teachers_router.callback_query(F.data == "root_teacher")
async def teacher_start_call(callback:CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    await start_teacher(message=callback.message)


@teachers_router.callback_query(F.data.startswith("teachers_less_"))
async def print_students(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[2]
    kb_list = []
    students = await get_students_ID_by_teacher_ID(teach_id=int(data))
    for student in students:
        stud_info = await get_student_by_id(id_stud=student[0])
        kb_list.append([InlineKeyboardButton(text=f"{stud_info[1]} {stud_info[2]}", callback_data=f"t_{student[0]}_{data}")])
    kb_list.append([InlineKeyboardButton(text="Добавить ученика", callback_data=f"admin_new_stud_{data}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"root_teacher")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(f"Выберите ученика:", reply_markup=kb)


@teachers_router.callback_query(F.data.startswith("t_"))
async def work_with_student(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[1:]
    student_info = await get_student_by_id(id_stud=int(data[0]))
    lesson_info = await get_lesson_by_IDS(id_stud=int(data[0]), id_teach=int(data[1]))
    past_lessons = lesson_info[3].split(",")
    if past_lessons != ['']:
        last_lessons = lesson_info[2] - len(lesson_info[3].split(","))
    else:
        last_lessons = 0
    text = f"{student_info[1]} {student_info[2]}\n\n{student_info[4]}\nтел: {student_info[5]}\n"
    text += "_______________\n"
    if last_lessons < 0:
        text += f"Неоплачено: {last_lessons * (-1)}"
    elif last_lessons > 0:
        text += f"Оплачено: {last_lessons}"
    else:
        text += f"Уроки закончились!!!"
    kb_list = [[InlineKeyboardButton(text="Подтвердить посещение",
                              callback_data=f"te_date_{student_info[0]}_{lesson_info[1]}")]]
    if student_info[6] != "":
        kb_list.append([InlineKeyboardButton(text="Связаться в TELEGRAM", url=f"tg://openmessage?user_id={student_info[6]}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"teachers_less_{data[1]}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text=text, reply_markup=kb)


@teachers_router.callback_query(F.data.startswith("te_date_"))
async def teacher_chose_date(callback: CallbackQuery):
    await callback.message.delete()
    kb_list = []
    data = callback.data.split("_")[2:]
    teach_id = await get_lesson_by_IDS(id_stud=int(data[0]), id_teach=int(data[1]))
    start_week = dt.datetime.today() - dt.timedelta(days=dt.datetime.now().date().weekday())
    for i in range(7):
        text = f"{(start_week + dt.timedelta(days=i)).strftime('%d.%m.%Y')}"
        kb_list.append([InlineKeyboardButton(text=text, callback_data=f"te_add_{data[0]}_{data[1]}_{text}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"t_{data[0]}_{teach_id[1]}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer("Выберите дату:", reply_markup=kb)


@teachers_router.callback_query(F.data.startswith("te_add_"))
async def teacher_add_lesson(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[2:]
    lesson_info = await get_lesson_by_IDS(id_stud=int(data[0]), id_teach=int(data[1]))
    past_lessons = lesson_info[3].split(",")
    print(past_lessons)
    if past_lessons != ['']:
        last_lessons = lesson_info[2] - len(past_lessons)-1
    else:
        last_lessons = lesson_info[2]-1
    print(last_lessons)
    if await add_lesson(id_stud=int(data[0]), id_teach=int(data[1]), date=data[2]):
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Главное меню", callback_data=f"teachers_less_{lesson_info[1]}")]])
        await callback.message.answer(text="Урок записан!\n/teacher", reply_markup=kb)
        if last_lessons < 2:
            teacher_info = await get_teacher_by_id(id_teach=int(data[1]))
            chat_id = await get_student_by_id(id_stud=int(data[0]))
            if chat_id[6] != '':
                text = f"По уроку '{teacher_info[2]}' у педагога '{teacher_info[1]}'\n"
                if last_lessons == 1:
                    text += "Остался 1 урок"
                if last_lessons == 0:
                    text += "Закончились уроки"
                if last_lessons < 0:
                    text += f"Образовался долг в размере {last_lessons*(-1)} урок(ов)"
                await bot.send_message(chat_id=chat_id[6], text=text)
    else:
        await callback.message.answer(text="Что-то пошло не так!!!(((\n/teacher")


@teachers_router.callback_query(F.data.startswith("get_results_"))
async def print_result(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")
    print(data)
    for t in teachers.keys():
        if teachers[t] == int(data[2]):
            t_name = t
    text = await print_results(teacher_name=t_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"root_teacher")]])
    await callback.message.answer(text=text, reply_markup=kb)
