import dataclasses

from vk import get_chat_name


@dataclasses.dataclass
class Texts:
    start_text = "start 123" # TODO
    invalid_token = "invalid token or anything else"
    select_chats = "select chats"


def generate_chat_info_text(chat):
    """Начало текста с информацией о сообщениях с чата"""
    return f'У вас новые сообщения в [чате {get_chat_name(chat=chat)}](https://vk.com/im?sel={chat.chat_id}). '
