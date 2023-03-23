import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from pocketbase import PocketBase

from models import Adhoc, Regular


class PocketbaseApi:
    load_dotenv()
    client = PocketBase(os.getenv("POCKETBASEIP"))

    def _respond_reg(self, inp):
        self.refresh_regular()

    def refresh_regular(self):
        self.regular_list.clear()
        result = self.client.collection("regular").get_full_list(200, {'sort': '-created'})
        for res in result:
            self.regular_list.append(
                Regular(res.__getattribute__('id'), res.__getattribute__('day'), res.__getattribute__('hour')
                        , res.__getattribute__('minute'), res.__getattribute__('title'),
                        res.__getattribute__('picture'), res.__getattribute__('audio'), res.__getattribute__('device'),
                        res.__getattribute__('options'),
                        datetime.strptime(res.__getattribute__('last_activated'),
                                          '%Y-%m-%d %H:%M:%S.%f')
                        if res.__getattribute__('last_activated') != '' else None,
                        datetime.strptime(res.__getattribute__('last_started'),
                                          '%Y-%m-%d %H:%M:%S.%f')
                        if res.__getattribute__('last_started') != '' else None))

    def _respond_adhoc(self, inp):
        self.refresh_adhoc()

    def refresh_adhoc(self):
        self.adhoc_list.clear()
        result = self.client.collection("adhoc").get_full_list(200, {'sort': '-created'})
        for res in result:
            if res.__getattribute__('activated') == '':
                self.adhoc_list.append(Adhoc(res.__getattribute__('id'), res.__getattribute__('title'),
                                             datetime.strptime(res.__getattribute__('when'), '%Y-%m-%d %H:%M:%S.%f'),
                                             res.__getattribute__('picture'), res.__getattribute__('options'),
                                             res.__getattribute__('audio'), res.__getattribute__('device'),
                                             res.__getattribute__('started'), res.__getattribute__('activated')))

    def _respond_config(self, inp):
        self.refresh_config()

    def refresh_config(self):
        result = self.client.collection("config").get_full_list(200)
        for res in result:
            self.config_list.update({res.__getattribute__('field'): res.__getattribute__('value')})

    def update_minutes(self, mins: int):
        result = self.client.collection("config").get_full_list(200)
        dat = {
            'value': mins
        }
        for res in result:
            if res.__getattribute__('field') == 'toothbrushminutes':
                self.client.collection("config").update(res.__getattribute__('id'), dat)

    def __init__(self):
        self.regular_list = []
        self.adhoc_list = []
        self.config_list = {}
        self.refresh_adhoc()
        self.refresh_regular()
        self.refresh_config()

        self.client.realtime.subscribe('regular', self._respond_reg)
        self.client.realtime.subscribe('adhoc', self._respond_adhoc)
        self.client.realtime.subscribe('config', self._respond_config)
