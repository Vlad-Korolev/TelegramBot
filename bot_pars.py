# Запросы к web-приложению.
import requests
# Дата и время.
import datetime
# Для логирвания событий.
from bot_log import log
# Для считывания и перезаписи переменых в файл конфигурации.
from bot_conf import get_setting, update_setting
# Для работы с файлами
import os


# Путь к файлу конфигурации.
configFile = "config.ini"
# Переменная для хранения ссылки запросов.
urlSchedule = get_setting(configFile, "AVALON", "urlSchedule")
# Переменная для хранения даты последней выгрузки с сайта.
lastSchedule = get_setting(configFile, "AVALON", "lastSchedule")
# Переменная для хранения расписания на день.
scheduleDay = get_setting(configFile, "AVALON", "scheduleDay")



def check_match(date):
    '''
    
    '''
    # Указываем глобальные переменные.
    global urlSchedule
    global lastSchedule
    global scheduleDay
    first_date = date

    
    # Открываем файл с GET-ответом
    with open('Hash/avalon.html', 'r', encoding="utf-8") as file:

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

                        log(f'Расписание на {date} сформировано, сохранено в config.ini', 'bot_pars')
                        update_setting(configFile, "AVALON", "lastschedule", first_date)
                        update_setting(configFile, "AVALON", "scheduleDay", schedule)
                        
                        # Возвращаем расписание.
                        return(schedule)           

            # прерываем цикл, если дата не найдена.
            if not line:
                # Увеличиваем полученныую дату на 1 день.
                # (ищем ближайщий день с занятиями)
                res = datetime.datetime.strptime(date, "%d.%m.%Y")
                date = (res + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
                log(f'Ищем ближайщий день {date}', 'bot_pars')
                # Возвращаем указатель на начало файла.
                file.seek(0)
  
            
def schedule(current_date):
    '''
    
    '''
    # Указываем глобальные переменные.
    global urlSchedule, lastSchedule, scheduleDay

    log(f'Запрос расписание на {current_date}', 'bot_pars')
    
    # Условие выполняется только в том случае, если дата полученная current_date == дате последней выгрузке расписания.
    if current_date == lastSchedule:
        schedule = scheduleDay
        log(f'Расписание на {current_date} найдено в хэше', 'bot_pars')
        return(schedule)
    else:
        log(f'Расписание на {current_date} в хэше не найдено', 'bot_pars')

    # Обрабатываем отправку GET-запроса по адресу университета. 
    try:
        # GET-запрос
        r = requests.get(urlSchedule)
        log(f'GET-запрос к AVALON, получение расписания на {current_date} выполнен успешно', 'bot_pars')
        # Условие: данная дериктория есть в наличии
        if not os.path.exists("Hash"):
            os.mkdir('Hash')
        # Создание файла.
        with open('Hash/avalon.html', 'w', encoding="utf-8") as file:
            # Запись ответана GET-запрос в файл.
            file.write(r.text)
            log(f'Результат GET-запроса сохранен в файл.', 'bot_pars')
            
    except:
        schedule = 'Расписание недоступно.'
        log(f'GET-запрос на получение расписания {current_date} не выполнен', 'bot_pars')
        return(schedule)

    schedule = check_match(current_date)
    return(schedule)
    
     

# Условие: файл запускается самостоятельно (не импортирован в виде модуля).
if __name__ == '__main__': 
    now = (datetime.datetime.now()).strftime("%d.%m.%Y")
    print(schedule('24.11.2022'))
    #print(schedule(now))
