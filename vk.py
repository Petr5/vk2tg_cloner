import vkbottle
from vkbottle import API


def get_user_data(token: str)-> dict:
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
