import logging

import vkbottle
from vkbottle import API

from db import User, Chat
from texts import generate_chat_info_text, new_message_text

log = logging.getLogger(__name__)


def get_user_data(token: str) -> dict:
    """get user data from vk api. Example:{'bdate': '1.9.2001',
         'bdate_visibility': 1,
         'city': BaseCity(id=1, title='Moscow'),
         'connections': None,
         'country': BaseCountry(id=1, title='Russia'),
         'first_name': 'Alina',
         'home_town': '',
         'interests': None,
         'languages': None,
         'last_name': 'Fedorova',
         'maiden_name': '',
         'name_request': None,
         'personal': None,
         'phone': '+7 *** *** ** 32',
         'relation': <UsersUserRelation.not_specified: 0>,
         'relation_partner': None,
         'relation_pending': None,
         'relation_requests': None,
         'screen_name': None,
         'sex': <BaseSex.female: 1>,
         'status': '',
         'status_audio': None,
         'can_access_closed': None,
         'deactivated': None,
         'hidden': None,
         'id': 738501706,
         'is_closed': None,
         'is_service_account': None,
         'photo_200': None}
"""
    api = API(token=token)
    return dict(await api.account.get_profile_info())


def get_user_chats(token: str = None, api=None, count=10, offset=0) -> dict:
    """get user chats from vk api. Required token or api instance.
    Example:{'count': 1,
         'items': [{'admin_level': 0,
                    'id': 1,
                    'is_closed': False,
                    'is_member': True,
                    'is_admin': False,
                    'name': 'Москва',
                    'photo_200': 'https://vk.com/images/community_200.png?ava=1',
                    'photo_200_orig': 'https://vk.com/images/community_200.png?ava=1',
                    'photo_max': 'https://vk.com/images/community_200.png?ava=1',
                    'photo_max_orig': 'https://vk.com/images/community_200.png?ava=1',
                    'screen_name': 'moscow',
                    'type': 'group'}]}
    """
    if api is None and token is None:
        raise ValueError("token or api is required")
    if api is None:
        api = API(token=token)
    return dict(await api.messages.get_conversations(count=count, offset=offset))


def get_chat_name(token: str = None, api: API = None, chat_id: int = None, chat: Chat = None, session=None) -> str:
    """get chat name from vk api. Required token and api instance.    """
    if token is None is None and chat is None:
        raise ValueError("token or api or chat instance is required")
    if chat is None and chat_id is None:
        raise ValueError("chat_id or chat is required")
    if chat is None and session is None:
        raise ValueError("session or chat is required")
    if chat is None:
        pass  # TODO
        # chat = session.query(Chat).filter_by(chat_id=chat_id, user).first()
    return ""  # TODO


def check(user: User, session): # TODO Придумать более адекватное название для функции и перенести ее в другой файлик
    """Проверить получение новых сообщений пользователем token (Но не более 150). Возвращает строку - сообщение. Если
    ничего новго возврщает None. """
    api = API(token=user.vk_token)
    info_text = None  # Уведомления пользователя о новых сообщениях
    user_chats = session.query(Chat).filter_by(user_id=user.id).all()
    for chat in user_chats:
        chat_history = dict(await api.messages.get_history(peer_id=chat.chat_id), count=150).get('items')
        if chat_history and len(chat_history) > 0:
            info_text = generate_chat_info_text(chat)
            for message in chat_history:
                if message['id'] != chat.last_message_id:
                    info_text += new_message_text(message)
                else:
                    break
            chat.last_message_id = message.id  # TODO Понять почему локальная переменная message может быть переназначена перед использованием
    session.commit()
    return info_text
