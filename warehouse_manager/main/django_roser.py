import os
from requests import Session
import datetime
import time
import json


class RoseRocket:
    def __init__(self):
        self.s = Session()
        self.login_post_url = os.environ.get('ROSER_LOGIN_POST_URL')
        self.login_creds = os.environ.get('ROSER_LOGIN_CREDS')
        self.login_creds = json.loads(self.login_creds)
        print(self.login_creds)
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

    def get_active_manifests(self):
        self.login()
        self.manifest_url = os.environ.get('ROSER_MANIFEST_URL')
        params = {'in_master_trip_status_ids': 'planning,assigned,moving',
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
        file = []
        for order in reply['data']['master_trip']['orders']:
            file.append(order['pop_file_url'])

        for stop in reply_pic['data']['stops']:
            for task in stop['tasks']:
                for files in task['task_files']:
                    file.append(files['url'])
        return file

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


if __name__ == '__main__':
    r = RoseRocket()
    manifests = r.get_active_manifests()
    for man in manifests:
        time.sleep(2)
        print(r.get_manifest_files(man['id']))
