from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardRemove
from utils.buliders import profile
from utils.states import Form
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import logging
import asyncio 
import json
import os

# Путь к файлу JSON базы данных
database_file = "user_profiles.json"

# Функция для загрузки данных из JSON файла
def load_database():
    if os.path.exists(database_file):
        with open(database_file, "r", encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = {}
    else:
        data = {}
    return data


# Функция для сохранения данных в JSON файл
def save_database(data):
    with open(database_file, "w", encoding='utf-8') as file:
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

# Здесь инициализируем базу данных
load_database()

# Инициализация бота и админки и другого
admin_id = 'Your ID'
bot = Bot(token='Your token', parse_mode='HTML')
dp = Dispatcher()
rmk = ReplyKeyboardRemove()


# Чтоб узнать когда бот будет запущен 
async def start_bot(bot: Bot): 
    await bot.send_message(admin_id, 'Бот запущен')

# Handlers 
@dp.message(Command('start'))
async def get_started(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_profile = get_user_profile(user_id)

    if user_profile:
        # Пользователь уже создал анкету, предоставьте ему доступ к действиям
        await message.answer(f'Привет, {message.from_user.first_name}. Вы уже создали анкету. Выбери, что ты хочешь',
                            reply_markup=profile(['Список команд', 'Анкета', 'Редактировать анкету', 'Поиск анкет']))
    else:
        # Пользователь еще не создал анкету, начнем процесс создания
        await message.answer("Привет, вы еще не создали анкету. Давайте начнем создание анкеты.")
        await state.set_state(Form.name)
        await message.answer('Введи своё имя', reply_markup=profile(message.from_user.first_name))


@dp.message(Command('show_profile'))
@dp.message(F.text.lower().strip() == 'анкета')
async def show_profile(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_profile = get_user_profile(user_id)

    if user_profile:
        formatted_text = []
        for key, value in user_profile.items():
            formatted_text.append(f'{key} - {value}')
        photo_file_id = user_profile.get("photo")
        formatted_text = formatted_text[:-1]

        # Отправить фотографию и анкету пользователя в одном сообщении
        if photo_file_id:
            await message.answer_photo(photo=photo_file_id, caption='\n'.join(formatted_text))
        else:
            await message.answer('\n'.join(formatted_text))
    else:
        await message.answer("Вы еще не создали анкету. Давайте начнем создание анкеты.")



@dp.message(Command('help'))
@dp.message(F.text.lower().strip() == 'список команд')
async def get_started(message: Message, state: FSMContext):
    help = '/start - На главную\n'
    help += '/show_profile - Посмотреть на свой профиль\n'
    help += '/profile - Сделать профиль\n'
    help += '/help - Список команд\n'
    help += '/search - Начать поиск\n'

    await message.answer(help)


@dp.message(Command('profile'))
@dp.message(F.text.lower().strip() == 'редактировать анкету')
async def fill_profile(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer('Введи своё имя', reply_markup=profile(message.from_user.first_name))


@dp.message(Command('search'))
@dp.message(F.text.lower().strip() == 'поиск анкет')
async def fill_profile(message: Message, state: FSMContext):
    await message.answer('В разработке')


# Handlers для создания профиля  
@dp.message(Form.name)
async def form_name(message: Message, state: FSMContext): 
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer('Введи свой возраст', reply_markup=rmk)

@dp.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=message.text)
        await state.set_state(Form.sex)
        await message.answer('Какой у тебя пол?', reply_markup=profile(['Мужской', 'Женский']))
    else:
        await message.answer('Неправильный формат данных')

@dp.message(Form.sex)
async def form_sex(message: Message, state: FSMContext): 
    text = message.text.strip().casefold()
    if text in ['мужской', 'женский']:
        await state.update_data(sex=text)
        await state.set_state(Form.about)
        await message.answer('Расскажи о себе', reply_markup=rmk)
    else:
        await message.answer('Пожалуйста, выбери пол, введя "мужской" или "женский".')



@dp.message(Form.about)
async def form_about(message: Message, state: FSMContext): 
    if len(message.text) < 5: 
        await message.answer('Ну попробуй что-то написать')
    else: 
        await state.update_data(about=message.text)
        await state.set_state(Form.photo)
        await message.answer('Теперь отправь фото')

@dp.message(Form.photo, F.photo)
async def form_about(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_file_id = message.photo[-1].file_id

    
    user_id = str(message.from_user.id)
    
    user_profile = {
        "name": data.get("name", ""),
        "age": data.get("age", ""),
        "sex": data.get("sex", ""),
        "about": data.get("about", ""),
        "photo": photo_file_id
    }

    # Сохраняем анкету пользователя в базе данных
    add_user_profile(user_id, user_profile)
    await state.clear()

    formatted_text = []
    [
        formatted_text.append(f'{key} - {value}')
        for key, value in data.items()
    ]
    await message.answer_photo(photo_file_id, '\n'.join(formatted_text))



async def main(): 
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s - [%(levelname)s] - %(name)s"
                                "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(start_bot)
    try: 
        await dp.start_polling(bot)
    finally: 
        await bot.session.close()

if __name__ == '__main__': 
    asyncio.run(main())