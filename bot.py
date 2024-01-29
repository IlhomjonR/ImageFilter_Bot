import logging
from aiogram import Dispatcher, Bot, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from database import *
from btns import *
from states import *
from utilis import *
import os

BOT_TOKEN = "6586055609:AAHn91sTlLeK1IoZxJ0U3OrpoBiOmBFFabI"

logging.basicConfig(level=logging.INFO)


bot = Bot(token=BOT_TOKEN, parse_mode='html')
storage = MemoryStorage()
ADMINS = [1116934049]
dp = Dispatcher(bot=bot, storage=storage)


async def set_commands(dp: Dispatcher):
    await create_tables()
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Ishga tushirish")
        ]
    )


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    btn = await start_btn()
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    await message.answer(f"Salom {message.from_user.first_name}", reply_markup=btn)


@dp.message_handler(commands=['stat'])
async def get_user_stat_commad(message: types.Message):
    if message.from_user.id in ADMINS:
        count = await get_all_users()
        await message.answer(f"Bot a'zolar soni: {count} ta")


@dp.message_handler(text="✨ Rasm Effect berish")
async def effect_to_image_handler(message: types.Message):
    btn = await filter_btn(filters)
    await message.answer("Filterlardan birini tanlang:", reply_markup=btn)


@dp.message_handler(text="Back⏭️")
async def back_handler(message: types.Message):
    await start_command(message)


@dp.message_handler(state=UserStates.get_image, content_types=['photo', 'text'])
async def get_image_handler(message: types.Message, state: FSMContext):
    content = message.content_type

    if content == "text":
        await effect_to_image_handler(message)
    else:
        file_name = f"Rasm_{message.from_user.id}.jpg"
        await message.photo[-1].download(destination_file=file_name)
        await message.answer("Rasm qabul qilindi ✅")

        data = await state.get_data()
        await filter_user_image(file_name, data['filter'])
        await message.answer_photo(
            photo=types.InputFile(file_name),
            caption=f"Rasm tayyor :)"
        )
        os.remove(file_name)
        await start_command(message)
    await state.finish()


@dp.message_handler(content_types=['text'])
async def selected_filters(message: types.Message, state: FSMContext):
    text = message.text

    if text in filters:
        await state.update_data(filter=text)
        btn = await cancel_btn()
        await message.answer("Rasmni yuboring:", reply_markup=btn)
        await UserStates.get_image.set()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=set_commands)
