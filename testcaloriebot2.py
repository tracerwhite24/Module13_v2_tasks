from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F

API = ''

bot = Bot(token=API)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Определение состояний пользователя
class UserState(StatesGroup):
    age = State()  # Ожидание ввода возраста
    growth = State()  # Ожидание ввода роста
    weight = State()  # Ожидание ввода веса


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью. Введите 'Calories', чтобы начать.")


@dp.message(F.text == "Calories")
async def set_age(message: types.Message, state: FSMContext):
    await state.set_state(UserState.age)  # Устанавливаем состояние ожидания возраста
    await message.answer("Введите свой возраст:")


@dp.message(UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)  # Сохраняем возраст
    await state.set_state(UserState.growth)  # Переходим к ожиданию роста
    await message.answer("Введите свой рост (в см):")


@dp.message(UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)  # Сохраняем рост
    await state.set_state(UserState.weight)  # Переходим к ожиданию веса
    await message.answer("Введите свой вес (в кг):")


@dp.message(UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)  # Сохраняем вес

    # Получаем все данные из состояния
    data = await state.get_data()
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула Миффлина - Сан Жеора для мужчин:
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f"Ваша норма калорий (BMR): {bmr:.2f} ккал.")

    await state.finish()  # Завершаем состояние


@dp.message()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == '__main__':
    import asyncio


    async def main():
        await dp.start_polling(bot)


    asyncio.run(main())













