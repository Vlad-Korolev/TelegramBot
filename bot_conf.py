import configparser, os
 
def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("TELEGRAM")
    config.set("TELEGRAM", "telegramaccesstoken", "5964465799:AAG-9zZOYOsNCfT_bGv-xV1xHTcyKJdO2k8")
    config.set("TELEGRAM", "telegramurl", "https://api.telegram.org/bot")

    config.add_section("LOG")
    config.set("LOG", "maxMessage", "10000")
    config.set("LOG", "messagecount", "0")
    config.set("LOG", "numberfilename", "1")

    config.add_section("AVALON")
    config.set("AVALON", "urlschedule", "https://www.avalon.ru/Retraining/GroupSchedule/18667/")
    config.set("AVALON", "lastschedule", "")
    config.set("AVALON", "scheduleday", "")

    with open(path, "w") as config_file:
        config.write(config_file)
        print(f"[bot_conf] Файл с конфигурацией {path} создан")
 

 
def get_config(path):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        print(f"[bot_conf] Файл с конфигурацией {path} не найден")
        create_config(path)
        
    config = configparser.ConfigParser()
    config.read(path)
    return config   
 

 
def get_setting(path, section, setting):
    """
    Print out a setting
    """
    config = get_config(path)
    value = config.get(section, setting)
    return value
 

 
def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "w") as config_file:
        config.write(config_file)
 

 
def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    config = get_config()
    config.remove_option(section, setting)
    with open(path, "w") as config_file:
        config.write(config_file)
 

 
if __name__ == "__main__":
    path = 'config.ini'
    get_config(path)
    




    

    
    