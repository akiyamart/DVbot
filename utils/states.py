from aiogram.fsm.state import StatesGroup, State

# Машина состояний для отслеживания прогресса заполнения анкеты
class Form(StatesGroup): 
    name = State()
    age = State()
    sex = State()
    about = State()
    photo = State()