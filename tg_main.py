import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import os
#tg_token = os.environ.get("TOKEN")
#

admins = [447392189, 1087504926]
teachers = {"Левон": 171392165, "Борис": 447392189, "Василина": 1087504926, "Ирина": 137375897, "Елена": 6586039437, "Марианна": 6188353707, "Татьяна": 401521989, "Вера":2038654204, "Анастасия":1362422567}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=tg_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


#137375897
