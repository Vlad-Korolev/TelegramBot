import datetime, os, zipfile
from bot_conf import get_setting, update_setting

path = "config.ini"
maxMessage     = int(get_setting(path, "LOG", "maxMessage"))
messageCount   = int(get_setting(path, "LOG", "messageCount"))
numberfileName = int(get_setting(path, "LOG", "numberfileName"))



def archive():
    '''
    
    '''
    global path, numberfileName
    
    try:
        archive = zipfile.ZipFile(f'log/bot_{numberfileName}.zip', 'w', zipfile.ZIP_DEFLATED)
        archive.write(f'log/bot_{numberfileName}.log')
        archive.close()
        os.remove(f'log/bot_{numberfileName}.log')
        
    except:
        print('[bot_log.py] ERROR Compressed')

    numberfileName += 1
    update_setting(path, "LOG", "numberfileName", str(numberfileName))
    


def log(text, event = 'Отладочное сообщение'):
    '''
    
    '''
    global path, maxMessage, messageCount, numberfileName

    now = datetime.datetime.now()
    currentDate = now.strftime("%d.%m.%Y %H:%M:%S")

    if not os.path.exists("log"):
        os.mkdir('Log')

    try:
        
        with open(f'log/bot_{numberfileName}.log', 'a+', encoding="utf-8") as logFile:
            messageCount += 1

            if event == 'GET' or event == 'POST' or event == 'СООБЩЕНИЕ':
                logMEssage = f'[{str(messageCount).rjust(6, "0")}][{currentDate}] [{event}]\n{text}'
                logFile.write(logMEssage + "\n") 
            else:
                logMEssage = f'[{str(messageCount).rjust(6, "0")}][{currentDate}] [{event}] {text}'
                logFile.write(logMEssage + "\n")  

    except FileNotFoundError:
        print("[FAIL] Don't write log file")
        
    if messageCount == maxMessage:
        messageCount = 0
        archive()
        log(f'Log-файл: {f"log/bot_{numberfileName - 1}.log"} заполнен, заархивирован: {f"log/bot_{numberfileName - 1}.zip"}. Создан новый: {f"log/bot_{numberfileName}.log"}', 'Bot_log.py')

    
    update_setting(path, "LOG", "messagecount", str(messageCount))


        
if __name__ == '__main__': 
    print('start')
    log('Test')



