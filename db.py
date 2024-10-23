import ast
import datetime, asyncio

import aiosqlite

from tg_main import teachers


async def get_lessons_by_stud_id(id_stud:int):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT * FROM lessons WHERE ID_stud='{id_stud}'")
    info = await cursor.fetchall()
    await cursor.close()
    await db.close()

    return info



async def get_student_by_family_and_name(family:str, name:str):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT * FROM students WHERE Family='{family}' AND Name='{name}'")
    info = await cursor.fetchone()
    await cursor.close()
    await db.close()

    return info[0]




async def get_all_lessons(where:str=None):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT * FROM lessons {where}")
    info = await cursor.fetchall()
    await cursor.close()
    await db.close()

    return info


async def get_lesson_by_IDS(id_stud:int, id_teach:int):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT * FROM lessons WHERE ID_stud={id_stud} AND ID_teach={id_teach}")
    info = await cursor.fetchone()
    await cursor.close()
    await db.close()

    return info


async def get_student_by_id(id_stud:int, column:str="*"):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT {column} FROM students WHERE ID={id_stud}")
    info = await cursor.fetchone()
    await cursor.close()
    await db.close()

    return info


async def get_teacher_by_id(id_teach:int, column:str="*"):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT {column} FROM teachers WHERE ID={id_teach}")
    info = await cursor.fetchone()
    await cursor.close()
    await db.close()

    return info


async def add_abonement(id_stud:int, id_teach:int, num_lessons:int):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT num_pay FROM lessons WHERE ID_stud={id_stud} AND ID_teach={id_teach}")
    info = await cursor.fetchone()
    result = await db.execute(f"UPDATE lessons SET num_pay={num_lessons+info[0]} WHERE ID_stud={id_stud} AND ID_teach={id_teach}")
    await db.commit()
    await cursor.close()
    await db.close()
    return True


async def add_lesson(id_stud:int, id_teach:int, date:str):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT past_lessons FROM lessons WHERE ID_stud={id_stud} AND ID_teach={id_teach}")
    info = await cursor.fetchone()
    if info[0]:
        past_lessons = info[0].split(",") + [date]
    else:
        past_lessons = [date]
    str_lessons = ""
    for dat in past_lessons:
        str_lessons += f"{dat},"
    print(str_lessons[:-1])
    result = await db.execute(f"UPDATE lessons SET past_lessons='{str_lessons[:-1]}' WHERE ID_stud={id_stud} AND ID_teach={id_teach}")
    await db.commit()
    await cursor.close()
    await db.close()
    return True


async def get_all_teachers_names():
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT teacher_name FROM teachers")
    info = list(await cursor.fetchall())
    await cursor.close()
    await db.close()

    return info


async def get_all_students(column:str="*"):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT {column} FROM students")
    info = list(await cursor.fetchall())
    await cursor.close()
    await db.close()

    return info


async def get_all_teachers(column:str="*"):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT {column} FROM teachers")
    info = list(await cursor.fetchall())
    await cursor.close()
    await db.close()

    return info


async def get_teacher_info(teach_name:str):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT lesson_name, ID FROM teachers WHERE teacher_name = '{teach_name}'")
    info = list(await cursor.fetchall())
    await cursor.close()
    await db.close()

    return info


async def get_students_ID_by_teacher_ID(teach_id:int):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT ID_stud FROM lessons WHERE ID_teach = '{teach_id}'")
    info = list(await cursor.fetchall())
    await cursor.close()
    await db.close()

    return info


async def get_students_by_tg_ids(tg_id, column:str="ID"):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"SELECT {column} FROM students WHERE tg_id='{tg_id}' ")
    info = list(await cursor.fetchall())
    await cursor.close()
    await db.close()

    return info


async def print_results(teacher_name=None, num_weeks:int=0):
    if teacher_name:
        teacher_lessons = await get_teacher_info(teach_name=teacher_name)
        teacher_ids = []
        for i in teacher_lessons:
            teacher_ids.append(i[1])
    lessons = []
    weekday = datetime.datetime.now().date().weekday()
    start_week_date = (datetime.datetime.today() - datetime.timedelta(days=int(weekday)+7*int(num_weeks)))
    days = [start_week_date.strftime("%d.%m.%Y")]
    day_zero = start_week_date
    for i in range(6):
        date = day_zero + datetime.timedelta(days=1)
        days.append(date.strftime("%d.%m.%Y"))
        day_zero = date


    all_lessons = await get_all_lessons()
    for less in all_lessons:
        for less_day in less[3].split(","):
            if less_day in days:
                if not teacher_name:
                    if less[3].split(",") != ['']:
                        last_lessons = less[2] - len(less[3].split(","))
                    else:
                        last_lessons = 0
                    student_info = await get_student_by_id(id_stud=int(less[0]))
                    teacher_info = await get_teacher_by_id(id_teach=int(less[1]))
                    lesson_dict = {
                            "FIO_stud": f"{student_info[1]} {student_info[2]}",
                            "teacher": f"{teacher_info[1]}",
                            "stavka": teacher_info[4],
                            "lesson": teacher_info[2],
                            "date": less_day,
                            "stoimost_for_stud":teacher_info[3],
                            "last_lessons":last_lessons,
                        }
                    if student_info[2] == "ПРОБНЫЙ УРОК":
                        lesson_dict["stavka"] = teacher_info[6]
                        lesson_dict["stoimost_for_stud"] = teacher_info[5]

                    if teacher_info[7] != "":
                        specials = (ast.literal_eval(teacher_info[7]))
                        if student_info[0] in specials:
                            lesson_dict["stavka"] = specials[student_info[0]][1]
                            lesson_dict["stoimost_for_stud"] = specials[student_info[0]][0]
                    lessons.append(
                        lesson_dict
                    )
                elif less[1] in teacher_ids:
                    if less[3].split(",") != ['']:
                        last_lessons = less[2] - len(less[3].split(","))
                    else:
                        last_lessons = 0
                    student_info = await get_student_by_id(id_stud=int(less[0]))
                    teacher_info = await get_teacher_by_id(id_teach=int(less[1]))
                    lesson_dict = {
                            "FIO_stud": f"{student_info[1]} {student_info[2]}",
                            "teacher": f"{teacher_info[1]}",
                            "stavka": teacher_info[4],
                            "lesson": teacher_info[2],
                            "date": less_day,
                            "stoimost_for_stud":teacher_info[3],
                            "last_lessons":last_lessons,
                        }
                    if student_info[2] == "ПРОБНЫЙ УРОК":
                        lesson_dict["stavka"] = teacher_info[6]
                        lesson_dict["stoimost_for_stud"] = teacher_info[5]

                    if teacher_info[7] != "":
                        specials = (ast.literal_eval(teacher_info[7]))
                        if student_info[0] in specials:
                            lesson_dict["stavka"] = specials[student_info[0]][1]
                            lesson_dict["stoimost_for_stud"] = specials[student_info[0]][0]
                    lessons.append(
                        lesson_dict
                    )
    message = f"\n\n\n{days[0]} - {days[-1]}\n\n"
    lessoms = sorted(lessons, key=lambda x: (x['teacher'], x['date'], x['FIO_stud']))
    if len(lessoms) != 0:
        if not teacher_name:
            message += lessoms[0]['teacher']
            message += ":\n"
        message += lessoms[0]['date']
        message += f"\n{lessoms[0]['FIO_stud']} : {lessoms[0]['stavka']} ({lessoms[0]['lesson']}) "
        if lessoms[0]["last_lessons"] < 0:
            message += f"Неоплачено: {lessoms[0]['last_lessons'] * (-1)}\n"
        elif lessoms[0]["last_lessons"] > 0:
            message += f"Оплачено: {lessoms[0]['last_lessons']}\n"
        else:
            message += f"Уроки закончились!!!\n"
        summ = lessoms[0]['stavka']
        vasil_commis = lessoms[0]['stoimost_for_stud']-lessoms[0]['stavka']
        for i in range(len(lessoms[1:])):
            if lessoms[i+1]['teacher'] != lessoms[i]['teacher']:
                message += "____________"
                teach_tg_id = teachers[lessoms[i]['teacher']]
                studs_on_teach_tg = await get_students_by_tg_ids(teach_tg_id)
                # У Учителя дети занимаются в студии
                if len(studs_on_teach_tg) != 0:
                    for stud in studs_on_teach_tg:
                        for lesson in await get_lessons_by_stud_id(id_stud=int(stud[0])):
                            if lesson[3] != '':
                                if lesson[2] < len(lesson[3].split(",")):
                                    stud_name = await get_student_by_id(id_stud=int(lesson[0]), column="Name")
                                    teach_info = await get_teacher_by_id(id_teach=lesson[1])
                                    print(teach_info[7])
                                    specials = {}
                                    if teach_info[7] != '':
                                        specials = (ast.literal_eval(teach_info[7]))
                                    if lesson[0] in specials.keys():
                                        s_com = specials[lesson[0]][0]
                                        t_com = specials[lesson[0]][1]
                                    else:
                                        s_com = teach_info[3]
                                        t_com = teach_info[4]
                                    summ -= int(s_com)
                                    message += f"\n{stud_name[0]} ({teach_info[2]}): -{s_com}"
                    message += "\n____________"
                message += f"\n{summ}"
                summ = 0
                message += "\n\n\n"
                message += lessoms[i+1]['teacher']
                message += ":\n"
            if lessoms[i+1]['date'] != lessoms[i]['date']:
                message += "\n"
                message += f"{lessoms[i+1]['date']}\n"
            message += f"{lessoms[i+1]['FIO_stud']} : {lessoms[i+1]['stavka']} ({lessoms[i+1]['lesson']}) "
            if lessoms[i+1]["last_lessons"] < 0:
                message += f"Неоплачено: {lessoms[i+1]['last_lessons'] * (-1)}\n"
            if lessoms[i+1]["last_lessons"] > 0:
                message += f"Оплачено: {lessoms[i+1]['last_lessons']}\n"
            if lessoms[i+1]["last_lessons"] == 0:
                message += f"Уроки закончились!!!\n"
            summ += lessoms[i+1]['stavka']
            vasil_commis += lessoms[i+1]['stoimost_for_stud'] - lessoms[i+1]['stavka']
        message += "____________"
        message += f"\n{summ}"
        if not teacher_name:
            message += f"\n\n\n_______________\nКОМИССИЯ СТУДИИ: {vasil_commis}\n__________________"
        return message
    else:
        return "На этой неделе уроков небыло"



async def get_new_student(info):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"INSERT INTO students (Family, Name, Birthday, Par_name, tel, tg_id, other) VALUES ('{info['family']}', '{info['name']}', '{info['birthday']}', '{info['name_parent']}', {info['num_telephone']}, '', '')")
    await db.commit()
    await cursor.close()
    await db.close()

    return info



async def write_st_ls(id_stud:int, id_teach:int):
    db = await aiosqlite.connect("db.db")
    cursor = await db.execute(f"INSERT INTO lessons (ID_stud, ID_teach, num_pay, past_lessons) VALUES ({id_stud}, {id_teach}, 0,  '')")
    await db.commit()
    await cursor.close()
    await db.close()

    return True



async def update_hi_mess(tg_id:int):
    db = await aiosqlite.connect("db.db")
    result = await db.execute(f"UPDATE students SET hi_mess=1 WHERE tg_id={tg_id}")
    await db.commit()
    await db.close()
    return True





#print(asyncio.run(print_results(num_weeks=(1))))



