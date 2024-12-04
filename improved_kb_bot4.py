from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging

API = ''

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Создание Inline-клавиатуры с двумя кнопками
button1 = InlineKeyboardButton(text="Рассчитать", callback_data="calculate")
button2 = InlineKeyboardButton(text="Информация", callback_data="info")
inline_kb = InlineKeyboardMarkup().add(button1, button2)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью. Выберите опцию:", reply_markup=inline_kb)

@dp.callback_query_handler(lambda c: c.data == "calculate")
async def set_age(callback_query: types.CallbackQuery):
    await UserState.age.set()
    await bot.send_message(callback_query.from_user.id, "Введите свой возраст:")

@dp.callback_query_handler(lambda c: c.data == "info")
async def info_command(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
                           "Этот бот поможет вам рассчитать вашу норму калорий. Нажмите 'Рассчитать', чтобы начать процесс расчета.")


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный возраст (число).")
        return

    await state.update_data(age=int(message.text))
    await UserState.growth.set()
    await message.answer("Введите свой рост (в см):")

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный рост (число).")
        return

    await state.update_data(growth=int(message.text))
    await UserState.weight.set()
    await message.answer("Введите свой вес (в кг):")

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный вес (число).")
        return

    await state.update_data(weight=int(message.text))

    # Получаем все данные из состояния
    data = await state.get_data()
    age = data.get('age')
    growth = data.get('growth')
    weight = data.get('weight')

    # Формула Миффлина - Сан Жеора для мужчин:
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f"Ваша норма калорий (BMR): {bmr:.2f} ккал.")

    await state.finish()

@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

