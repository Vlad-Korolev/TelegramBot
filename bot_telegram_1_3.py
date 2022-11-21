# Запросы к web-приложению (API).
import requests
# Преобразование.
import json
# Использования файла конфигурации.
from configparser import ConfigParser 
# Используем функцию 'log' из модуля 'bot_log' (находится в корневой папке)
from bot_log import log


# Переменная для работы 'ConfigParser'.
config = ConfigParser() 
# Прочесть файла конфигурации.
config.read('config.ini')

# Переменная для хранения Токена телеграмм (прочитан с файла).
telegramAccessToken = config.get('TELEGRAM', 'telegramAccessToken')
# Переменная для хранения ссылки запросов (прочитана с файла).
telegramUrl = config.get('TELEGRAM', 'telegramUrl')

# ====================== Функции ======================
def main():
    '''
        Основная функция для работы скрипта, производит запуск остальных ф-ций.
    '''

    # Переменная для хранения 'id_update'(необходим для отправки на сервер при long-Pooling).
    # (на оснеовании 'id_update' сервер понимает, какой последний update мы получили).
    offset = -1

    while True:
        # Ф-ция для записи сообщений в log-файл
        log('Отправлен GET-запрос на получение обновлений')

        # Обрабатываем отправку запроса GET (получаем последние события).
        try:
            # Параметры запроса
            params = {
                       'timeout': 30,       # Сервер держит соединения 30 секунд (Long-Pooling), при появлении ответа сразу его высылает.
                        'offset': offset    # 'id_update', следующий после последнего полученного.
                     }
            # Запрос (get) на получения последнего события.
            r = requests.get(
                                f"{telegramUrl}{telegramAccessToken}/getUpdates",
                                data = params
                            )
            # Переменная для хранения ответа от  сервера в json.
            data = r.json()
            # Ф-ция для записи сообщений в log-файл
            log('Запрос GET-выполнен успешно (Long-Pooling)')
            # Ответ запроса в удобном для чтения формате .json
            log((json.dumps(data, indent = 4)), 'GET')
        # В случае неудачного запроса (при ошибке).
        except: 
            # Ф-ция для записи сообщений в log-файл
            log('Запрос GET - не выполнен')
            # Возвращаемся в начало цикла While.
            continue

        # Условие выполняется только в том случае, если в ответе на GET запрос ['result]: пустой.
        if  not data['result']: 
            # Ф-ция для записи сообщений в log-файл
            log('Новых обновлений нет')
            # Возвращаемся в начало цикла While.
            continue
        
        # Условие выполняется только в том случае, если внутри ответа на GET запрос есть ключ 'message'.
        if 'message' in data['result'][0]:

            # Условие выполняется только в том случае, если внутри ответа на GET запрос есть ключ 'text'.
            if 'text' in data['result'][0]['message']:
                # Ф-ция для записи сообщений в log-файл
                log('Внутри GET-ответа в "result" найден "message"')
                # Переменная для хранения имени пользователя.
                userName = data['result'][0]['message']['from']['username']
                # Переменная для хранения сообщении пользователя.
                userMessage = data['result'][0]['message']['text']
                # Переменная для хранения даты отправки сообщения пользователем.
                userMessageDate = data['result'][0]['message']['date']
                # Переменная для хранения ID-чата с пользователем.
                userChatId = data['result'][0]['message']['chat']['id']
                # Переменная для хранения типа чата
                chatType = data['result'][0]['message']['chat']['type']

                 # Условие выполняется только в том случае, если внутри ответа на GET запрос (['result'][0]['message']['chat']) есть ключ 'title'.
                if 'title' in data['result'][0]['message']['chat']:
                    # Переменная для хранения имени чата
                    chatTitle = data['result'][0]['message']['chat']['title']
                    # Ф-ция для записи сообщений в log-файл
                    log(f'Тип чата: {chatType}\nНазвание чата: {chatTitle}\nПользователь: {userName}\n"{userMessage}"', 'СООБЩЕНИЕ') 

                else:
                    # Ф-ция для записи сообщений в log-файл
                    log(f'Тип чата: {chatType}\nПользователь: {userName}\n{userMessage}', 'СООБЩЕНИЕ')              

                # Обрабатываем отправку запроса POST (отправляем пользователю ответ на сообщение).
                try:
                    # Параметры запроса.
                    params = {
                                "chat_id": userChatId,     
                                    "text": userMessage   
                                }
                    # # Запрос (post) на отправку сообщения пользователю.
                    r = requests.post(
                                        f"{telegramUrl}{telegramAccessToken}/sendMessage",
                                        data = params
                                    ).json()
                    # Ф-ция для записи сообщений в log-файл
                    log('Запрос POST-отправлен успешно')
                    # Запрос POST в удобном для чтения формате .json
                    log((json.dumps(r, indent = 4)), 'POST')

                # В случае неудачного запроса (при ошибке)
                except: 
                    # Ф-ция для записи сообщений в log-файл
                    log('Запрос POST-не отправлен')
                    pass

            # Переменная для хранения 'id_update'(необходим для отправки на сервер при long-Pooling),
            # (на оснеовании 'id_update' сервер понимает, какой последний update мы получили),
            # увеличиваем 'id_update' на 1 от последнего полученного.
            offset = data['result'][0]['update_id'] + 1

        # При невыполнении условия: "внутри ответа на GET запрос есть ключ 'message'".
        else:
            # Ф-ция для записи сообщений в log-файл
            log('Внутри GET-ответа в "message" не найден ключ: "text"')
            # Переменная для хранения 'id_update'(необходим для отправки на сервер при long-Pooling),
            # (на оснеовании 'id_update' сервер понимает, какой последний update мы получили),
            # увеличиваем 'id_update' на 1 от последнего полученного.
            offset = data['result'][0]['update_id'] + 1
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

        

            
