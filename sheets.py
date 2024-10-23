import ast
import datetime
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
import asyncio

from db import get_teacher_info, get_all_lessons, get_student_by_id, get_teacher_by_id

spreadsheet_id_all = '1wjRh7AYwpcCqbD2JUhe3cjAs9IOs9tDifK4bNmqfV3w'

# COLORS
green = {'red': 0.8509804, 'green': 0.91764706, 'blue': 0.827451}
# COLORS


def color_sheets(mass="Лист5!A2:AZ201"):
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'google.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = spreadsheet_id_all

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
    return service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=mass,
        includeGridData=True
    ).execute()


def get_all_students(mass="Лист5!A2:C"):
    return color_sheets(mass=mass)['sheets'][0]['data'][0]['rowData']


def read_sheets(range:str, rows_columns="ROWS"):
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'google.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = spreadsheet_id_all

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
    values = (service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range,
        majorDimension=rows_columns,
        # includeGridData=True
    ).execute())
    return values


def paint_cell(row: int, column: int, color: dict, num_rows: int = 1, num_colums: int = 1):
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'google.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = spreadsheet_id_all

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
    resp = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=["Лист5"],
                                                 includeGridData=False).execute()
    sheet_id = resp.get("sheets")[0].get("properties").get("sheetId")
    body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row,
                        "startColumnIndex": column,
                        "endColumnIndex": column+num_colums,
                        "endRowIndex": row+num_rows,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": color,
                        },
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            }
        ]
    }
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()



def len_last_lessons(first_column, sheet, student:str, teacher:str, lesson:str):
    # Находим нужную строчку

    for i in range(len(first_column)):
        if 'formattedValue' in first_column[i]['values'][0].keys():
            if first_column[i]['values'][0]['formattedValue'] == student:
                if first_column[i]['values'][1]['formattedValue'] == teacher:
                    if first_column[i]['values'][2]['formattedValue'] == lesson:
                        row_stud = i


    not_pay_lessons = 0
    will_lessons = 0
    try:
        temp = sheet[row_stud]['values']
    except:
        print(first_column, sheet, student, teacher, lesson)
    for cell in temp[5:-1]:
        try:
            if "formattedValue" in cell:
                if cell["userEnteredFormat"]['backgroundColor'] == {'red': 1, 'green': 1, 'blue': 1}:
                    not_pay_lessons += 1
            else:
                if cell["userEnteredFormat"]['backgroundColor'] != {'red': 1, 'green': 1, 'blue': 1}:
                    will_lessons += 1
        except:
            print(student, teacher, lesson, temp.index(cell))
            break
    return {"not_pay":not_pay_lessons, "will_lessons": will_lessons}



async def print_results(teacher_name=None, num_weeks:int=0):
    if teacher_name:
        teacher_lessons = await get_teacher_info(teach_name=teacher_name)
        teacher_ids = []
        for i in teacher_lessons:
            teacher_ids.append(i[1])
    lessons = []
    weekday = datetime.datetime.now().date().weekday()
    start_week_date = (datetime.datetime.today() - datetime.timedelta(days=int(weekday)+1+7*int(num_weeks)))
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
                if less[3].split(",") != ['']:
                    last_lessons = less[2] - len(less[3].split(","))
                else:
                    last_lessons = 0
                print(last_lessons)
                student_info = await get_student_by_id(id_stud=int(less[0]))
                teacher_info = await get_teacher_by_id(id_teach=int(less[1]))
                if not teacher_name:
                    lessons.append(
                        {
                            "FIO_stud": f"{student_info[1]} {student_info[2]}",
                            "teacher": f"{teacher_info[1]}",
                            "stavka": teacher_info[4],
                            "lesson": teacher_info[2],
                            "date": less_day,
                            "stoimost_for_stud":teacher_info[3],
                            "last_lessons":last_lessons,
                        }
                    )
                elif less[1] in teacher_ids:
                    lessons.append(
                        {
                            "FIO_stud": f"{student_info[1]} {student_info[2]}",
                            "teacher": f"{teacher_info[1]}",
                            "stavka": teacher_info[4],
                            "lesson": teacher_info[2],
                            "date": less_day,
                            "stoimost_for_stud":teacher_info[3],
                            "last_lessons":last_lessons,
                        }
                    )
                if student_info[2] == "ПРОБНЫЙ УРОК":
                    lessons[-1]["stavka"] = teacher_info[6]
                    lessons[-1]["stoimost_for_stud"] = teacher_info[5]
                if teacher_info[7] != "":
                    specials = (ast.literal_eval(teacher_info[7]))
                    if student_info[0] in specials:
                        lessons[-1]["stavka"] = specials[student_info[0]][1]
                        lessons[-1]["stoimost_for_stud"] = specials[student_info[0]][0]
                print(lessons[-1])
    #print(lessons)

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



def add_lessons(student:str, teacher:str, lesson:str, num_less_add:int):
    first_column = get_all_students()
    sheet = color_sheets()['sheets'][0]['data'][0]['rowData']
    for i in range(len(first_column)):
        if 'formattedValue' in first_column[i]['values'][0].keys():
            if first_column[i]['values'][0]['formattedValue'] == student:
                if first_column[i]['values'][1]['formattedValue'] == teacher:
                    if first_column[i]['values'][2]['formattedValue'] == lesson:
                        row_stud = i
                        break
    for i in range(len(sheet[row_stud]['values'][5:])):
        if "backgroundColor" not in sheet[row_stud]['values'][i+5]["userEnteredFormat"] or sheet[row_stud]['values'][i+5]["userEnteredFormat"]["backgroundColor"]['red'] == 1:
            start_column = i+5
            break
    paint_cell(row=row_stud+1, color=green, num_colums=num_less_add, num_rows=2, column=start_column)
    return True


def print_lesson(row:int, column:int, date:str):
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'google.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = spreadsheet_id_all

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
    body = {'values' : [
        [date], [2]
    ]}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Лист5!{chr(int(column) + 64)}{row}",
        valueInputOption="RAW",
        body=body
    ).execute()
    return True



def temp():
    sheets = read_sheets(range="Лист5!F2:M112")['values']
    t = []
    for i in range(1, int(len(sheets)/2+2)):
        #t.append(sheets[i*2-2])
        print(str(sheets[i*2-2])[1:-1].replace("'","").replace(" ",""))
    #return len(t)




#print(asyncio.run(print_results(num_weeks=1)))