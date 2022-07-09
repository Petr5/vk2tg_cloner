import asyncio

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import exceptions

import logging
import config
from db import User, get_or_create, engine
from utils import get_token_from_url, list_of_dict_to_list
from texts import Texts
import aiogram
from sqlalchemy.orm import sessionmaker
from vk import get_user_data, get_user_chats

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
    # TODO Логика если сообщение не пролазит по длине
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
    await send_message(message.chat.id, Texts.start)
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
    except IndexError or VKAPIError_5:  # TODO Эот ексепшн вызывается при попытке использования неправильного токена
        await send_message(message.chat.id, Texts.invalid_token)
        log.warning(f"Invalid token from user {message.user.id}")
        return
    user.status = "select_chats"
    user.has_valid_token = True
    user.vk_page_id = user_data["id"]
    user.vk_page_name = user_data["first_name"] + " " + user_data["last_name"]
    session.add(user)
    session.commit()
    await Register.select_chats.set()
    # await send_message(message.chat.id, Texts.select_chats(user))
    # TODO Логика выбора чатов с отображением клавиатуры


@dp.message_handler(state=Register.select_chats)
async def add_chats(message):
    pass


# TODO Тут должна

@dp.message_handler(commands=['add'])
async def add_chat_by_id(message):
    """Добвить чат пользователя если он явным образом указывает его id, вот так /add 123456789"""
    # TODO на всех подобного рода командах добавить проверку что пользователь уже ввел токен
    user = session.query(User).filter_by(telegram_id=message.chat.id, has_valid_token=True).first()
    if user is None:
        await send_message(message.chat.id, Texts.start_text)
        return
    chats = get_user_chats(token=user.vk_token).get("items")
    if len(message.args) != 2:
        await send_message(message.chat.id, Texts.force_add_chat_help)
        return
    chat_id = message.args[1]
    if chat_id in list_of_dict_to_list(chats, "id"):
        await send_message(message.chat.id, Texts.chat_added_successfully(chat_id))
        return
    else:
        await send_message(message.chat.id, Texts.chat_not_found)
        log.warning(f"Chat not found, {user}, {chat_id}")


