import asyncio

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import exceptions

import logging
import config
from User import User, get_or_create, engine
from utils import get_token_from_url
from texts import texts
import aiogram
from sqlalchemy.orm import sessionmaker
from vk import get_user_data


bot = aiogram.Bot(token=config.telgram_token)
dp = aiogram.Dispatcher(bot)
session = sessionmaker(bind=engine)()
log = logging.getLogger("bot")


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive callвы
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


class Register(StatesGroup):
    waiting_for_vk_token = State()
    select_chats = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await send_message(message.chat.id, texts.start)
    user = get_or_create(session, User, telegram_id=message.chat.id)
    user.telegram_chat_id = message.chat.id
    user.status = "waiting_for_vk_token"
    await Register.waiting_for_vk_token.set()


@dp.message_handler(state=Register.waiting_for_vk_token)
async def waiting_for_vk_token(message):
    user = get_or_create(session, User, telegram_id=message.chat.id)
    try:
        user.vk_token = token = get_token_from_url(message.text)
        user_data = get_user_data(token)
    except IndexError or VKAPIError_5: # TODO Эот ексепшн вызывается при попытке использования неправильного токена
        await send_message(message.chat.id, texts.invalid_token)
        log.warning(f"Invalid token from user {message.user.id}")
        return
    user.status = "select_chats"
    user.vk_page_id = user_data["id"]
    user.vk_page_name = user_data["first_name"] + " " + user_data["last_name"]
    session.add(user)
    session.commit()
    await Register.select_chats.set()
    await send_message(message.chat.id, texts.select_chats(user))

@dp.message_handler(state=Register.select_chats)
async def register_