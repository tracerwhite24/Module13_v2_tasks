from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Пример использования
logging.info('Бот запущен')

API = ''

bot = Bot(token=API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class UserState(StatesGroup):
    age = State()  # Ожидание ввода возраста
    growth = State()  # Ожидание ввода роста
    weight = State()  # Ожидание ввода веса

# Создание Inline-клавиатуры
inline_button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_button_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_button_calories], [inline_button_formulas]])

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью. Выберите опцию:", reply_markup=inline_kb)

@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_message = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\n"
        "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formula_message)
    await call.answer()  # Убедитесь, что этот вызов есть

@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.age)
    await call.message.answer("Введите свой возраст:")
    await call.answer()  # Убедитесь, что этот вызов есть

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError
        await state.update_data(age=age)
        await state.set_state(UserState.growth)
        await message.answer("Введите свой рост (в см):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст.")

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        growth = int(message.text)
        if growth <= 0:
            raise ValueError
        await state.update_data(growth=growth)
        await state.set_state(UserState.weight)
        await message.answer("Введите свой вес (в кг):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный рост.")

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        if weight <= 0:
            raise ValueError
        await state.update_data(weight=weight)

        data = await state.get_data()
        age = data.get('age')
        growth = data.get('growth')
        weight = data.get('weight')

        # Формула Миффлина - Сан Жеора для мужчин:
        bmr = 10 * weight + 6.25 * growth - 5 * age + 5

        await message.answer(f"Ваша норма калорий (BMR): {bmr:.2f} ккал.")
        await state.finish()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный вес.")

@dp.message_handler(lambda message: message.text == "Информация")
async def info_command(message: types.Message):
    await message.answer("Этот бот поможет вам рассчитать норму калорий и предоставит информацию о формуле расчета.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)





