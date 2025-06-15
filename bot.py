from aiogram import executor
from handlers import dp
import config, db  # чтобы инициализировать базу
from aiogram.contrib.fsm_storage.memory import MemoryStorage
config.dp.storage = MemoryStorage()  # подключаем FSM

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
