import datetime

def log(text, event = 'Отладочное сообщение'):
    # Переменная для хранения текущей даты и времени
    now = datetime.datetime.now()
    # Отформатированная дата вида: [21.11.2022 02:31:36] 
    currentDate = now.strftime("%d.%m.%Y %H:%M:%S")
    
    with open('bot.log', 'a+', encoding="utf-8") as logFile:

        if event == 'GET' or event == 'POST':
            logMEssage = f'[{currentDate}] [{event}]\n{text}'
            logFile.write('\n' + logMEssage)

        elif 'СООБЩЕНИЕ' in event:
            logMEssage = f'[{currentDate}] [{event}]\n{text}'
            logFile.write('\n' + logMEssage)
            
        else:
            logMEssage = f'[{currentDate}] [{event}] {text}'
            logFile.write('\n' + logMEssage)

