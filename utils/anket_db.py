import json
import os

# Путь к файлу JSON базы данных
database_file = "user_profiles.json"

# Функция для загрузки данных из JSON файла
def load_database():
    if os.path.exists(database_file):
        with open(database_file, "r") as file:
            data = json.load(file)
        return data
    else:
        return {}

# Функция для сохранения данных в JSON файл
def save_database(data):
    with open(database_file, "w") as file:
        json.dump(data, file, indent=4)

# Функция для добавления анкеты пользователя в базу данных
def add_user_profile(user_id, profile_data):
    database = load_database()
    database[user_id] = profile_data
    save_database(database)

# Функция для получения анкеты пользователя из базы данных
def get_user_profile(user_id):
    database = load_database()
    return database.get(user_id, {})

