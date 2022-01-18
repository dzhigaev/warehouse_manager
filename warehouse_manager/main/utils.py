from .models import *
from requests import Session


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        return context


# class Roser(Session):
#     get_url = 'https://millhouse.roserocket.com'
#     post_url = 'https://millhouse.roserocket.com/api/v1/sessions'
#     login_creds = {'email': 'ftlupdates@millhouse.com',
#                    'password': 'Millhouse_21'}
#     def __init__(self):
#         super().__init__()
