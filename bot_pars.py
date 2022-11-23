# Запросы к web-приложению.
import requests
# Дата и время
import datetime
# Использования файла конфигурации.
from configparser import ConfigParser 
# Использования регулярных выражений.
import re
# Используем функцию log из модуля bot_log (находится в корневой папке). Для логирвоаняи событий
from bot_log import log


# Переменная для работы 'ConfigParser'.
config = ConfigParser() 
# Прочесть файла конфигурации.
config.read('config.ini')
# Переменная для хранения ссылки запросов (прочитана с файла).
urlSchedule = config.get('AVALON', 'urlSchedule')
# Переменная для хранения даты выгрузки и парсинга расписания с сайта
lastSchedule = config.get('AVALON', 'lastSchedule')
# Переменная для хранения расписания на день
scheduleDay = config.get('AVALON', 'scheduleDay')

def check_match(date):
    '''
    
    '''
    # Указываем глобальные переменные.
    global urlSchedule
    global lastSchedule
    global scheduleDay
    first_date = date
    
    # Открываем файл с GET-ответом
    with open('avalon.html', 'r', encoding="utf-8") as file:

        while True:
            # считываем строку
            line = file.readline()

            # Условие выполняется только в том случае, date найдена в line.
            if date in line:
                
                # Переменные для хранения расписания
                lblTime = 'default'
                lblClassType = 'default'
                lblClassroom = 'default'
                lblCourse = 'default'
                lblTeacher = 'default'

                while True:
                    # считываем строку
                    line = file.readline()

                    if 'id="lblTime"' in line:
                        lblTime = (line.strip()).replace('<span id="lblTime" data-format="{0:t} - {1:t}">','')
                        lblTime = lblTime.replace('</span>','')
                    elif 'id="lblClassType"' in line:
                        lblClassType = (line.strip()).replace('<span id="lblClassType" data-format="{0}">','')
                        lblClassType = lblClassType.replace('</span>','')
                    elif 'id="lblClassroom"' in line:
                        lblClassroom = (line.strip()).replace('<span id="lblClassroom" data-format="{0}">','')
                        lblClassroom = lblClassroom.replace('</span>','')
                    elif 'id="lblCourse"' in line:
                        lblCourse = (line.strip()).replace('<span id="lblCourse" data-format="{0}">','')
                        lblCourse = lblCourse.replace('</span>','')
                    elif 'id="lblTeacher"' in line:
                        lblTeacher = (line.strip()).replace('<span id="lblTeacher" data-format="{0}">','')
                        lblTeacher = lblTeacher.replace('</span>','')

                        if first_date == date:
                            # Переменная для хранения сформированного текста с расписанием.
                            schedule = f'[{date}]\n{lblTime}\n{lblClassType}\n{lblClassroom}\n{lblCourse}\n{lblTeacher}'
                        else:
                            # Переменная для хранения сформированного текста с расписанием.
                            schedule = f'[{first_date}]\nЗанятий нету,\nближайшее занятие:\n\n[{date}]\n{lblTime}\n{lblClassType}\n{lblClassroom}\n{lblCourse}\n{lblTeacher}'

                        # Записываем текущее расписание в config.ini.
                        config.set('AVALON', 'scheduleDay',  schedule)
                        config.write(open('config.ini', "w"))
                        # Записываем дату выгрузки и парсинга расписания с сайта в config.ini.
                        config.set('AVALON', 'lastSchedule',  first_date)
                        config.write(open('config.ini', "w"))
                        
                        log(f'Расписание {date} сформировано', 'bot_pars')
                        # Возвращаем расписание.
                        return(schedule)           

            # прерываем цикл, если дата не найдена.
            if not line:
                # Увеличиваем полученныую дату на 1 день.
                # (ищем ближайщий день с занятиями)
                res = datetime.datetime.strptime(date, "%d.%m.%Y")
                date = (res + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
                log(f'{date} занятий нет, ищем ближайщий день', 'bot_pars')
                # Возвращаем указатель на начало файла.
                file.seek(0)
  
            
def schedule(current_date):
    '''
    
    '''
    # Указываем глобальные переменные.
    global urlSchedule
    global lastSchedule
    global scheduleDay

    log(f'Запрос на расписание {current_date}', 'bot_pars')
    
    # Условие выполняется только в том случае, если дата полученная current_date == дате последней выгрузке расписания.
    if current_date == lastSchedule:
        schedule = scheduleDay
        log(f'Расписание {current_date} найдено в хэше', 'bot_pars')
        return(schedule)

    # Обрабатываем отправку GET-запроса по адресу университета. 
    try:
        # GET-запрос
        r = requests.get(urlSchedule)
        # Создание файла.
        with open('avalon.html', 'w', encoding="utf-8") as file:
            # Запись ответана GET-запрос в файл.
            file.write(r.text)
            log('GET-запрос на получение расписания {current_date} выполнен успешно', 'bot_pars')
    except:
        schedule = 'Расписание недоступно.'
        log('GET-запрос на получение расписания {current_date} не выполнен', 'bot_pars')
        return(schedule)

    schedule = check_match(current_date)
    return(schedule)
     

# Условие: файл запускается самостоятельно (не импортирован в виде модуля).
if __name__ == '__main__': 
    now = (datetime.datetime.now()).strftime("%d.%m.%Y")
    print(schedule('22.11.2022'))