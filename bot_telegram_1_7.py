# Запросы к web-приложению (API).
import requests
# Преобразование.
import json
# Дата и время
import datetime
# Использования файла конфигурации.
from configparser import ConfigParser 
# Используем функцию log из модуля bot_log (находится в корневой папке). Для логирвоаняи событий
from bot_log import log
# Используем функцию schedule из модуля bot_pars (находится в корневой папке). Для полученяи расписания
from bot_pars import schedule


# Переменная для работы 'ConfigParser'.
config = ConfigParser() 
# Прочесть файла конфигурации.
config.read('config.ini')

# Переменная для хранения Токена телеграмм (прочитан с файла).
telegramAccessToken = config.get('TELEGRAM', 'telegramAccessToken')
# Переменная для хранения ссылки запросов (прочитана с файла).
telegramUrl = config.get('TELEGRAM', 'telegramUrl')
# Переменная для хранения 'id_update'(необходим для отправки на сервер при long-Pooling),
# на основании 'id_update' сервер понимает, какой последний update мы получили.
offset = -1

# ====================== Функции ======================
def check_message(response):
    '''
        Функция check_message(response) проверяет полученный message, ищет соответствия.
            В качестве аргумента ожидает:
            "response" - ответ от GET-запроса.
        Функция ничего не возвращает.
    '''
    # Указываем, что 'offset' является глобальной переменной 
    global offset

    # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][message] есть ключ: [text].
    if 'text' in response[0]['message']:
        # Ф-ция для записи сообщений в log-файл
        log('Внутри GET-ответа [0][message] найден [text]')
        
        # Переменные для хранения необходимых значений.
        update_id = response[0]['update_id']
        userMessage = response[0]['message']['text']
        userMessageDate = response[0]['message']['date']
        chat_id = response[0]['message']['chat']['id']
        chatType = response[0]['message']['chat']['type']


        # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][message][from] есть ключ: [username].
        # От сервера может вернуться ответ без ключа username но с ключом: first_name.
        if 'username' in response[0]['message']['from']:
            userName = response[0]['message']['from']['username']
        else:
            userName = response[0]['message']['from']['first_name']


        # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][message][chat] есть ключ: [title].
        # title присутствует у публичных чатов
        if 'title' in response[0]['message']['chat']:
            chatTitle = response[0]['message']['chat']['title']
            # Ф-ция для записи сообщений в log-файл.
            log(f'ПОЛУЧЕНИЕ\nТип чата: {chatType}\nНазвание чата: {chatTitle}\nПользователь: {userName}\n"{userMessage}"', 'СООБЩЕНИЕ') 
        else:
            # Ф-ция для записи сообщений в log-файл.
            log(f'ПОЛУЧЕНИЕ\nТип чата: {chatType}\nПользователь: {userName}\n"{userMessage}"', 'СООБЩЕНИЕ')              


        # Условие выполняется только в том случае, если внутри ответа на GET-запрос [message][text] есть текст /start.
        if '/start' in response[0]['message']['text']:
            # Ф-ция для записи сообщений в log-файл.
            log('В [message][text] найдено совпадение по ключу: "/start"')

            # Отправляем в ответ приветствие, меню.
            # Ф-ция для записи сообщений в log-файл
            log('"Отправляем в ответ приветствие и меню"')
            # Метод запроса.
            req_url = "sendMessage"
            # Параметры запроса.
            req_param = {"chat_id": chat_id,     
                            "text": "Готов к работе!",
                    "reply_markup": json.dumps({"inline_keyboard": [[{
                                                                                    "text" : "Расписание",
                                                                           "callback_data" : "schedule"}]]})}
            # Ф-ция для отправки POST-запроса на сервер.
            request_post(req_url, req_param, update_id)


            # Условие выполняется только в том случае, если внутри ответа на GET-запрос [message][text] есть текст /day.
        if '/day' in response[0]['message']['text']:
            # Ф-ция для записи сообщений в log-файл.
            log('В [message][text] найдено совпадение по ключу: "/day"')

           # Переменная для хранения текущей даты и времени
            now = (datetime.datetime.now()).strftime("%d.%m.%Y")
            # Вызываем ф-цию для получения расписания (записываем ответ в переменную)
            scheduleCurrentDate = schedule(now)
    
            # Отправка расписание занятий на сегодня.
            log('Отправляем расписание на сегодня в чат')
            # Метод запроса.
            req_url = "sendMessage"
            # Параметры запроса.
            req_param = {"chat_id": chat_id,     
                            "text": scheduleCurrentDate}
            # Ф-ция для отправки POST-запроса на сервер.
            request_post(req_url, req_param, update_id)


    # При невыполнении условия: внутри ответа на GET-запрос [0][message] есть ключ: [text].
    else:
        # Ф-ция для записи сообщений в log-файл
        log('Внутри GET-ответа [result][0][message] не найден ключ: [text]')
    
    # Увеличиваем id_update на 1 от последнего полученного,
    # тем самым указывая серверу, что ждем следующее за этим обновление.
    offset = update_id + 1



def check_callback(response):
    '''
        Функция check_callback(response) проверяет полученный callback, ищет соответствия.
            В качестве аргумента ожидает:
            "response" - ответ от GET-запроса.
        Функция ничего не возвращает.
    '''
    # Указываем, что offset является глобальной переменной 
    global offset

    # Переменные для хранения необходимых значений.
    update_id = response[0]['update_id']
    callback_id = response[0]['callback_query']['id']
    collback_data = response[0]['callback_query']['data']
    chat_id = response[0]['callback_query']['message']['chat']['id']
    message_id = response[0]['callback_query']['message']['message_id']
    
    # Проверки на соответствия ключам:
    
    # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][callback_query][data] есть текст: schedule.
    if 'schedule' in collback_data:
        # Ф-ция для записи сообщений в log-файл.
        log('[0][callback_query][data] совпадение по тексту: schedule')

        # Ф-ция для записи сообщений в log-файл.
        log('Совпадение по тексту: schedule: отправляем уведомление в чат')
        # Отправка уведомления в чат.
        # Метод запроса.
        req_url = "answerCallbackQuery"
        # Параметры запроса.
        req_param = {"callback_query_id": callback_id,     
                              "text": 'Узнать расписание занятий'}
        # Ф-ция для отправки POST-запроса на сервер.
        request_post(req_url, req_param, update_id)

        # Меняем меню ReplyMarkup и текст сообщения.
        # Ф-ция для записи сообщений в log-файл
        log('Совпадение по тексту: schedule: меняем меню ReplyMarkup и текст сообщения')
        # Метод запроса.
        req_url = "editMessageText"
        # Параметры запроса.
        req_param = {"chat_id": chat_id,     
                    "message_id": message_id,
                    "text": "Что посмотреть?",
                    "reply_markup": json.dumps({"inline_keyboard": [[{
                                                                                        "text":"Расписание на сегодня", 
                                                                              "callback_data" : "currentDateSchedule"}],
                                                                    [{
                                                                                        "text":"Расписание по дате", 
                                                                              "callback_data" : "weekDateSchedule"}],
                                                                    [{
                                                                                        "text":"Полное расписание", 
                                                                                         "url": "https://www.avalon.ru/Retraining/GroupSchedule/18667/"}],
                                                                    [{
                                                                                        "text":"Закрыть", 
                                                                                         "callback_data" : "closeReply_markup"}]]})}

        # Ф-ция для отправки POST-запроса на сервер.
        request_post(req_url, req_param, update_id)


    # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][callback_query][data] есть текст: currentDateSchedule.
    if 'currentDateSchedule' in collback_data:
        # Переменная для отправки сообщения в log.
        log('[0][callback_query][data] совпадение по тексту: currentDateSchedule')

        # Переменная для хранения текущей даты и времени
        now = (datetime.datetime.now()).strftime("%d.%m.%Y")
        # Вызываем ф-цию для получения расписания (записываем ответ в переменную)
        scheduleCurrentDate = schedule(now)
 
        # Отправка расписание занятий на сегодня.
        log('Совпадение по тексту: currentDateSchedule: отправляем расписание на сегодня в чат')
        # Метод запроса.
        req_url = "sendMessage"
        # Параметры запроса.
        req_param = {"chat_id": chat_id,     
                        "text": scheduleCurrentDate}
        # Ф-ция для отправки POST-запроса на сервер.
        request_post(req_url, req_param, update_id)

        # Удаление сообщения с ReplyMarkup
        # Ф-ция для записи сообщений в log-файл
        log('Совпадение по тексту: currentDateSchedule: удаляем предыдущее сообщение')
        # Запрос на удаление сообщения.
        # Метод запроса.
        req_url = "deleteMessage"
        # Параметры запроса.
        req_param = {   "chat_id": chat_id,     
                        "message_id": message_id}
        # Ф-ция для отправки POST-запроса на сервер.
        request_post(req_url, req_param, update_id)


    # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][callback_query][data] есть текст: weekDateSchedule.
    if 'weekDateSchedule' in collback_data:
        # Ф-ция для записи сообщений в log-файл.
        log('[0][callback_query][data] совпадение по тексту: weekDateSchedule')

        # Меняем меню ReplyMarkup и текст сообщения.
        # Ф-ция для записи сообщений в log-файл
        log('Совпадение по тексту: weekDateSchedule: меняем меню ReplyMarkup и текст сообщения')
        # Метод запроса.
        req_url = "editMessageText"
        # Параметры запроса.
        req_param = {    "chat_id": chat_id,     
                      "message_id": message_id,
                            "text": "Временно недоступно :(",
                    "reply_markup": json.dumps({"inline_keyboard": [[{
                                                                                  "text":"Назад", 
                                                                        "callback_data" : "schedule"}]]})}
        # Ф-ция для отправки POST-запроса на сервер.
        request_post(req_url, req_param, update_id)   



    # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0][callback_query][data] есть текст: closeReply_markup.
    if 'closeReply_markup' in collback_data:
        # Ф-ция для записи сообщений в log-файл.
        log('[0][callback_query][data] совпадение по тексту: closeReply_markup')  

        # Удаление сообщения с ReplyMarkup
        # Ф-ция для записи сообщений в log-файл
        log('Совпадение по тексту: closeReply_markup: удаляем сообщение')
        # Запрос на удаление сообщения.
        # Метод запроса.
        req_url = "deleteMessage"
        # Параметры запроса.
        req_param = {   "chat_id": chat_id,     
                        "message_id": message_id}
        # Ф-ция для отправки POST-запроса на сервер.
        request_post(req_url, req_param, update_id)        



def request_post(req_url,  req_param, update_id):
    '''
        Функция 'request_post(req_url, req_param, update_id)', отправляет post-запросы на сервер.
            В качестве аргументов ожидает:
            "req_url" - метод запроса;
            "req_param" - параметры запроса;
            "update_id" - id последнего полученного обновления.
        Функция ничего не возвращает.

    '''
    # Указываем, что offset является глобальной переменной 
    global offset

    # Обрабатываем отправку POST-запроса (отправляется в json формате).
    try:
        r = requests.post(
                            f"{telegramUrl}{telegramAccessToken}/{req_url}",
                            data = req_param
                         ).json()
        # Ф-ция для записи сообщений в log-файл
        log('Запрос POST-отправлен успешно')
        # Запрос POST в удобном для чтения формате .json
        log((json.dumps(r, indent = 4)), 'POST')
    # В случае неудачного запроса (при ошибке)
    except: 
        # Ф-ция для записи сообщений в log-файл
        log('Запрос POST-не отправлен')
        
    # Увеличиваем id_update на 1 от последнего полученного,
    # тем самым указывая серверу, что ждем следующее за этим обновление.
    offset = update_id + 1



def request_get():
    '''
        Функция 'request_get()', отправляет get-запросы на сервер.
            В качестве аргументов ничего не ожидает:
        Функция возвращает:
            return(data) - ответ на get-запрос.

    '''
    # Указываем, что offset является глобальной переменной 
    global offset 

    # Цикл на оправку GET-запроса.
    while True:    
        # Ф-ция для записи сообщений в log-файл
        log('Отправка GET-запроса на получение обновлений')

        # Обрабатываем отправку GET-запроса (получаем новые обновления, отправляется в json формате).
        try:
            # Параметры запроса
            req_params = {
                        'timeout': 30,       # Сервер поддерживает соединения 30 секунд (Long-Pooling), при появлении ответа сразу его высылает.
                        'offset': offset     # 'id_update'.
                        }
            # Get-запрос 
            r = requests.get(
                                f"{telegramUrl}{telegramAccessToken}/getUpdates",
                                data = req_params
                            ).json()
            # Переменная для хранения ответа от  сервера в json.
            data = r['result']
            # Ф-ция для записи сообщений в log-файл
            log('GET-запрос выполнен успешно')
            # Ответ запроса в удобном для чтения формате json
            log((json.dumps(r, indent = 4)), 'GET')
        # В случае неудачного запроса (при ошибке).
        except: 
            # Ф-ция для записи сообщений в log-файл
            log('GET-запрос не выполнен')
            continue

        # Условие выполняется только в том случае, если в ответе на GET-запрос [result][0]: пустой.
        if  not data: 
            # Ф-ция для записи сообщений в log-файл
            log('Новых обновлений нет')
            # Возвращаемся в начало цикла While.
            continue

        # Возвращаем ответ на GET-запрос
        return(data)



def main():
    '''
        Основная функция для работы скрипта, производит запуск остальных функций.
    '''
    # Указываем, что offset является глобальной переменной 
    global offset

    while True:
        # Вызываем ф-цию для отправки get-запроса на получение обновлений.
        data = request_get()
                    
        # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0] есть ключ: [callback_query].
        if 'callback_query' in data[0]:
            # Ф-ция для записи сообщений в log-файл.
            log('В GET-запросе [0] получен ключ [callback_query]')
            # Вызываем ф-цию для проверки [callback].
            check_callback(data)
                

        # Условие выполняется только в том случае, если внутри ответа на GET-запрос [0] есть ключ: [message].
        if 'message' in data[0]:
            # Ф-ция для записи сообщений в log-файл.
            log('В GET-запросе получен "message"')
            # Вызываем ф-цию для проверки [message].
            check_message(data)
        else:
            # Ф-ция для записи сообщений в log-файл
            log('Внутри GET-ответа в [0] не найден ключ: [message]')
            # увеличиваем 'id_update' на 1 от последнего полученного.
            offset = data[0]['update_id'] + 1
            # Возвращаемся в начало цикла While.
            continue
            
# Условие: файл запускается самостоятельно (не импортирован в виде модуля).
if __name__ == '__main__':
    # Обработка исключений
    try:
        print('Bot начал работу\nЛог записывается в "bot.log"')
        # Запускаем выполнения основной ф-ции.
        main()
    # исключение на 'ctrl+c'
    except KeyboardInterrupt:
        exit()

        

            
