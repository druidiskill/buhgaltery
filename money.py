from db import get_all_lessons, get_teacher_by_id
import asyncio


async def main():
    bank = 0
    dolg = 0
    for lesson in await get_all_lessons():
        teacher = await get_teacher_by_id(id_teach=lesson[1])
        num_last_lessons = lesson[2] - len(lesson[3].split(","))
        if lesson[3] =='':
            num_last_lessons = lesson[2]
        stavka = teacher[3]
        if lesson[0] not in [23,44]:
            if num_last_lessons > -1:
                bank += stavka * num_last_lessons
            else:
                dolg += stavka * num_last_lessons

    return (f"BANK = {bank}\nДОЛГ = {dolg*(-1)}")



if __name__ == "__main__":
    print(asyncio.run(main()))
