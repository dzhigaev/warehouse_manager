import os
from requests import Session
import datetime
import json

from django.utils import timezone

from .models import RRToken


class RoseRocket:
    def __init__(self):
        self.s = Session()
        self.login_post_url = os.environ.get('ROSER_LOGIN_POST_URL')
        self.login_creds = os.environ.get('ROSER_LOGIN_CREDS')
        self.login_creds = json.loads(self.login_creds)
        self.s.headers.update({
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/90.0.4430.212 Safari/537.36"})
        self.today = datetime.datetime.now()
        self.last_week = self.today - datetime.timedelta(days=7)
        self.next_week = self.today + datetime.timedelta(days=7)
        self.today = datetime.datetime.strftime(self.today, '%Y-%m-%dT00:00:00-05:00')
        self.last_week = datetime.datetime.strftime(self.last_week, '%Y-%m-%dT00:00:00-05:00')
        self.next_week = datetime.datetime.strftime(self.next_week, '%Y-%m-%dT00:00:00-05:00')

    def login(self):
        rr_token = RRToken.objects.last()
        if rr_token.login_time + datetime.timedelta(
                seconds=rr_token.expiary_date
        ) < timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()):
            self.post = self.s.post(self.login_post_url, headers=self.s.headers, json=self.login_creds).json()
            self.data = str(self.post["data"]["token_type"]) + " " + str(self.post["data"]["token"])
            self.s.headers.update({
                "content-type": "application/json",
                "accept": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/90.0.4430.212 Safari/537.36",
                "authorization": self.data,
                "x-datadog-trace-id": "4823135534527647769",
                "x-datadog-parent-id": "3792996712835868751"
            })
            new_token = RRToken(token=str(self.post["data"]["token"]),
                                expiary_date=self.post['data']['expires_in'])
            new_token.save()
        else:
            self.data = rr_token.token
            self.s.headers.update({
                "content-type": "application/json",
                "accept": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/90.0.4430.212 Safari/537.36",
                "authorization": f'Bearer {self.data}',
                "x-datadog-trace-id": "4823135534527647769",
                "x-datadog-parent-id": "3792996712835868751"
            })
            me_try = self.s.get('https://millhouse.roserocket.com/api/v1/me', headers=self.s.headers).json()
            if me_try.get('data') is None:
                self.post = self.s.post(self.login_post_url, headers=self.s.headers, json=self.login_creds).json()
                self.data = str(self.post["data"]["token_type"]) + " " + str(self.post["data"]["token"])
                self.s.headers.update({
                    "content-type": "application/json",
                    "accept": "application/json",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/90.0.4430.212 Safari/537.36",
                    "authorization": self.data,
                    "x-datadog-trace-id": "4823135534527647769",
                    "x-datadog-parent-id": "3792996712835868751"
                })
                new_token = RRToken(token=str(self.post["data"]["token"]),
                                    expiary_date=self.post['data']['expires_in'])
                new_token.save()

    def get_active_manifests(self):
        self.login()
        self.manifest_url = os.environ.get('ROSER_MANIFEST_URL')
        params = {'in_master_trip_status_ids': 'planning,assigned,moving',
                  'time_start_at': f'{self.last_week}',
                  'time_end_at': f'{self.next_week}',
                  'time_relative_date': 'dateRange',
                  'sort': 'start_at asc',
                  'limit': '200',
                  'offset': '0'}
        return self.s.get(self.manifest_url, params=params, headers=self.s.headers).json()['data']

    def get_manifest_files(self, manifest_id):
        self.login()
        url = f"{os.environ.get('ROSER_MANIFEST_URL')}/{manifest_id}"
        url_pic = f"{os.environ.get('ROSER_MANIFEST_URL')}/{manifest_id}/stops"
        params = {'relations': 'orders'}
        reply = self.s.get(url, params=params, headers=self.s.headers).json()
        reply_pic = self.s.get(url_pic, headers=self.s.headers).json()
        load_file_dict = {}
        for order in reply['data']['master_trip']['orders']:
            load_file_dict[order['full_id']] = []
            load_file_dict[order['full_id']].append(order['pop_file_url'])

        for stop in reply_pic['data']['stops']:
            for task in stop['tasks']:
                for files in task['task_files']:
                    load_file_dict[task['order_full_id']].append(files['url'])
        return load_file_dict

    def get_manifest_by_number(self, search_term):
        self.login()
        url = os.environ.get('ROSER_MANIFEST_URL')
        params = {
            'search_term': str(search_term),
            'sort': 'start_at asc',
            'offset': 0,
            'limit': 100
        }
        return self.s.get(url, params=params, headers=self.s.headers).json()['data']

    def valid_token(self, token):
        print(self.s.get(os.environ.get('ROSER_LOGIN_POST_URL'), ))


if __name__ == '__main__':
    r = RoseRocket()
