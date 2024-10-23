from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.other import send_hi_mess
from money import main
from tg_main import bot, admins, teachers
import datetime as dt
from db import get_all_teachers_names, get_teacher_info, get_students_ID_by_teacher_ID, get_student_by_id, \
    get_teacher_by_id, get_lesson_by_IDS, add_abonement, print_results, get_new_student, get_all_students, \
    get_all_teachers, write_st_ls, get_all_lessons, get_student_by_family_and_name

admin_router = Router()


class new_student(StatesGroup):
    family = State()
    name = State()
    birthday = State()
    name_parent = State()
    num_telephone = State()
    lesson = None


@admin_router.callback_query(F.data.startswith("admin_new_stud"))
async def add_new_student(callback:CallbackQuery, state:FSMContext):
    data = callback.data.split("_")
    if len(data) == 4:
        await state.update_data(lesson=data[3])
    await callback.message.answer(text="Введите фамилию учащегося:")
    await state.set_state(new_student.family)



@admin_router.message(new_student.family)
async def add_student_name(message:Message, state:FSMContext):
    await state.update_data(family=message.text[0].upper()+message.text[1:].lower())
    await message.answer(text="Введите имя:")
    await state.set_state(new_student.name)



@admin_router.message(new_student.name)
async def add_student_bithday(message:Message, state:FSMContext):
    await state.update_data(name=message.text[0].upper()+message.text[1:].lower())
    await message.answer(text="Введите дату рождения в формате '01.01.2001':")
    await state.set_state(new_student.birthday)



@admin_router.message(new_student.birthday)
async def add_student_name_parent(message:Message, state:FSMContext):
    await state.update_data(birthday=message.text)
    await message.answer(text="Введите имя представителя:")
    await state.set_state(new_student.name_parent)



@admin_router.message(new_student.name_parent)
async def add_student_num_telephone(message:Message, state:FSMContext):
    await state.update_data(name_parent=message.text[0].upper()+message.text[1:].lower())
    await message.answer(text="Введите номер телефона представителя в формате '89991112233':")
    await state.set_state(new_student.num_telephone)



@admin_router.message(new_student.num_telephone)
async def add_student_finish(message:Message, state:FSMContext):
    await state.update_data(num_telephone=message.text)
    info = await state.get_data()
    print(info)
    await get_new_student(info)
    if "lesson" in info:
        print(info)
        ID = await get_student_by_family_and_name(family=info["family"], name=info["name"])
        print(await write_st_ls(id_stud=int(ID), id_teach=int(info["lesson"])))
    await message.answer(text="Ученик добавлен")
    await state.clear()



@admin_router.message(Command("admin"))
async def admin_start(message: Message):
    await message.delete()
    need_mess = await get_all_students()
    for stud in need_mess:
        if stud[6] != '':
            if stud[8] == 0:
                try:
                    await send_hi_mess(tg_id=int(stud[6]))
                except:
                    pass
    if int(message.chat.id) in admins:
        teachers_list = await get_all_teachers_names()
        teachers_kb_list = [[InlineKeyboardButton(text="РЕЗУЛЬТАТЫ НЕДЕЛИ", callback_data="results")]]
        for teacher in set(teachers_list):
            kb_btn = [InlineKeyboardButton(text=str(teacher[0]), callback_data=f"teach_{teacher[0]}")]
            teachers_kb_list.append(kb_btn)
        teachers_kb_list.append([InlineKeyboardButton(text="Добавить нового ученика", callback_data="admin_new_stud")])
        teachers_kb_list.append([InlineKeyboardButton(text="УЧЕНИК-УРОК", callback_data="adm_add_st_ls")])
        teachers_kb_list.append([InlineKeyboardButton(text="ДОЛЖНИКИ", callback_data="must_pay")])
        kb = InlineKeyboardMarkup(inline_keyboard=teachers_kb_list)
        await bot.send_message(text="Режим АДМИНИСТРАТОРА", chat_id=message.chat.id, reply_markup=kb)
    else:
        await message.answer("Вы не являетесь АДМИНИСТРАТОРОМ!!!")


@admin_router.callback_query(F.data == "root_admin")
async def admin_start_call(callback:CallbackQuery):
    await admin_start(message=callback.message)


@admin_router.callback_query(F.data == 'results')
async def print_results_tg(callback: CallbackQuery):
    await callback.message.delete()
    if int(callback.from_user.id) in admins:
        kb_list = []
        for i in range(4):
            start_week_date = dt.datetime.today() - dt.timedelta(days=dt.datetime.now().date().weekday()+1+7*i)
            kb_list.append([InlineKeyboardButton(text=f"{start_week_date.strftime('%d.%m.%Y')} - {(start_week_date + dt.timedelta(days=6)).strftime('%d.%m.%Y')}", callback_data=f"results_{i}")])
        kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"root_admin")])
        kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
        await callback.message.answer("Выберите неделю:", reply_markup=kb)

@admin_router.callback_query(F.data.startswith('results_'))
async def print_results_tg_on_week(callback: CallbackQuery):
    await callback.message.delete()
    num_week = callback.data.split("_")[1]
    await callback.message.answer(await print_results(num_weeks=int(num_week)))
    if int(num_week) == 0:
        if dt.datetime.now().date().weekday() in [6, 0]:
            for teacher in teachers.keys():
                await bot.send_message(chat_id=teachers[teacher], text=await print_results(teacher_name=teacher))

@admin_router.callback_query(F.data.startswith('teach_'))
async def print_lessons_of_teacher(callback: CallbackQuery):
    await callback.message.delete()
    teacher = callback.data.split("_")[1]
    kb_list = []
    for lesson in await get_teacher_info(teach_name=teacher):
        kb_list.append([InlineKeyboardButton(text=lesson[0], callback_data=f"less_{lesson[1]}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"root_admin")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer("Выберите урок", reply_markup=kb)


@admin_router.callback_query(F.data.startswith('less_'))
async def print_students_of_lesson(callback: CallbackQuery):
    await callback.message.delete()
    lesson = callback.data.split("_")[1]
    kb_list = []
    lesson_info = await get_teacher_by_id(id_teach=int(lesson))
    stud_ids = await get_students_ID_by_teacher_ID(teach_id=int(lesson))
    for student in stud_ids:
        stud_info = await get_student_by_id(id_stud=student[0])
        kb_list.append([InlineKeyboardButton(text=f"{stud_info[1]} {stud_info[2]}", callback_data=f"l_{student[0]}_{lesson}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"teach_{lesson_info[1]}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(f"{lesson_info[1]}\n{lesson_info[2]}", reply_markup=kb)


@admin_router.callback_query(F.data.startswith("l_"))
async def print_info_about_student(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[1:]
    kb_list = [[
        InlineKeyboardButton(text="Посмотреть историю уроков", callback_data=f"look_history_{data[0]}_{data[1]}")
    ],[
        InlineKeyboardButton(text="Добавить уроки", callback_data=f"give_less_{data[0]}_{data[1]}")
    ],[
        InlineKeyboardButton(text="Назад", callback_data=f"less_{data[1]}")
    ]]
    student_info = await get_student_by_id(id_stud=int(data[0]))
    lesson_info = await get_lesson_by_IDS(id_stud=int(data[0]), id_teach=int(data[1]))
    past_lessons = lesson_info[3].split(",")
    if past_lessons != ['']:
        last_lessons = lesson_info[2]-len(lesson_info[3].split(","))
    else:
        last_lessons = lesson_info[2]
    text = f"{student_info[1]} {student_info[2]}\n\n{student_info[4]}\nтел: {student_info[5]}\n"
    if student_info[6] != '':
        text += f"tg://openmessage?user_id={student_info[6]}\n"
    text += "_______________\n"
    if last_lessons < 0:
        text += f"Неоплачено: {last_lessons * (-1)}"
    elif last_lessons > 0:
        text += f"Оплачено: {last_lessons}"
    else:
        text += f"Уроки закончились!!!"
    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_list))


@admin_router.callback_query(F.data.startswith("add_"))
async def add_lessons_callback(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[1:]
    add_lessons_res = await add_abonement(id_stud=int(data[0]), id_teach=int(data[1]), num_lessons=int(data[2]))
    if add_lessons_res:
        await callback.message.answer(f"Добавлено {data[2]} урок(ов)")
        teacher_info = await get_teacher_by_id(id_teach=int(data[1]))
        student_info = await get_student_by_id(id_stud=int(data[0]))
        await bot.send_message(chat_id=teachers[teacher_info[1]], text=f"{student_info[1]} {student_info[2]}\n{teacher_info[2]}\nДобавдено {data[2]} урок(ов)")


@admin_router.callback_query(F.data == "adm_add_st_ls")
async def add_st_ls(callback:CallbackQuery):
    all_students = await get_all_students()
    kb_list = []
    for stud in all_students:
        kb_list.append([InlineKeyboardButton(text=f"{stud[1]} {stud[2]}", callback_data=f"a_s_l_{stud[0]}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text="Выберите ученика:", reply_markup=kb)


@admin_router.callback_query(F.data.startswith("a_s_l_"))
async def a_s_l(callback:CallbackQuery):
    data = callback.data.split("_")[-1]
    all_lessons = await get_all_teachers()
    kb_list = []
    for lesson in all_lessons:
        kb_list.append([InlineKeyboardButton(text=f"{lesson[1]} {lesson[2]}", callback_data=f"ad_s_l_{data}_{lesson[0]}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"adm_add_st_ls")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text="Выберите предмет и учителя::", reply_markup=kb)


@admin_router.callback_query(F.data.startswith("ad_s_l_"))
async def write_stud_less(callback:CallbackQuery):
    data = callback.data.split("_")[3:]
    student_info = await get_student_by_id(id_stud=int(data[0]))
    lesson_info = await get_teacher_by_id(id_teach=int(data[1]))
    result = await write_st_ls(id_stud=student_info[0], id_teach=lesson_info[0])
    if result:
        await callback.message.answer(text=f"{student_info[1]} {student_info[2]} успешно записан на занятие:\n{lesson_info[1]} {lesson_info[2]}")



@admin_router.callback_query(F.data.startswith("look_history_"))
async def look_history(callback:CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[2:]
    lesson_info = await get_lesson_by_IDS(id_stud=int(data[0]), id_teach=int(data[1]))
    past_lessons = lesson_info[3].split(",")
    text = "Прошлые уроки:\n\n"
    if past_lessons == ['']:
        past_lessons = []
    for less in past_lessons:
        text += f"{less}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"l_{data[0]}_{data[1]}")]])
    await callback.message.answer(text=text, reply_markup=kb)


@admin_router.callback_query(F.data.startswith("give_less_"))
async def get_lessons(callback:CallbackQuery):
    await callback.message.delete()
    data = callback.data.split("_")[2:]
    kb_list = [[InlineKeyboardButton(text=f"+1 урок", callback_data=f"add_{data[0]}_{data[1]}_1")]]
    for i in range(3):
        kb_list.append([InlineKeyboardButton(text=f"+{i+2} урока", callback_data=f"add_{data[0]}_{data[1]}_{i+2}")])
    for i in range(4):
        kb_list.append([InlineKeyboardButton(text=f"+{i+5} уроков", callback_data=f"add_{data[0]}_{data[1]}_{i+5}")])
    kb_list.append([InlineKeyboardButton(text="Назад", callback_data=f"l_{data[0]}_{data[1]}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await callback.message.answer(text="Выберите нужное кол-во:", reply_markup=kb)


@admin_router.callback_query(F.data == "must_pay")
async def must_pay(callback:CallbackQuery):
    await callback.message.delete()
    all_students  = await get_all_lessons()
    text = "ДОЛЖНИКИ:\n\n"
    temp = []
    for studen in all_students:
        teach_info = await get_teacher_by_id(id_teach=int(studen[1]))
        stud_info = await get_student_by_id(id_stud=int(studen[0]))
        pay_lessons = int(studen[2])
        if studen[3] != '':
            past_lessons = len(studen[3].split(","))
        else:
            past_lessons = 0
        family = stud_info[1]
        name = stud_info[2]+" "+str(stud_info[0])
        lesson = teach_info[2]+" "+str(teach_info[0])
        row = f"{family} {name} | {lesson} | "
        if pay_lessons < past_lessons:
            row += f"ДОЛГ:{past_lessons-pay_lessons}"
        elif pay_lessons - past_lessons == 0:
            row += f"Уроки закончились!!!"
        else:
            row += f"ОСТ: {pay_lessons - past_lessons}"
        row += "\n\n"
        temp.append({"last_pay":pay_lessons - past_lessons,"row":row})
    newlist = sorted(temp, key=lambda d: d['last_pay'])
    for row in newlist:
        text += f"{row['row']}"
    try:
        await callback.message.answer(text=text)
    except:
        half_text_num = int(len(text)/2)
        print(half_text_num)
        await callback.message.answer(text=text[:half_text_num])
        await callback.message.answer(text=text[half_text_num:])

    await callback.message.answer(text=await main())

