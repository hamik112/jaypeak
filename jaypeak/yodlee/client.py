import json
import logging
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from . import utils
from flask import Config


class Client(object):

    def __init__(self):
        self.config = Config(__name__)

    def login_cobrand(self):
        url = self.config['BASE_URL'] + "/cobrand/login"
        data = {
            'cobrandLogin': self.config['COBRAND_USERNAME'],
            'cobrandPassword': self.config['COBRAND_PASSWORD']
        }
        try:
            response = requests.post(url, data=data)
        except requests.exceptions.RequestException:
            message = 'Request url: {url}'.format(url=url)
            logging.error(message)
            raise

        utils.verify_json_response_or_raise_value_error(response)

        return response

    def login_user(self, cobrand_session_token, username, password):
        url = self.config['BASE_URL'] + "/user/login"
        data = {
            'loginName': username,
            'password': password,
        }
        headers = {
            'Authorization': '{{cobSession={}}}'.format(cobrand_session_token)
        }
        try:
            response = requests.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            message = (
                'Request url: {url}\n'
                'Request headers: {headers}\n'
            ).format(
                url=url,
                data=data,
                headers=headers,
            )
            logging.error(message)
            raise

        utils.verify_json_response_or_raise_value_error(response)

        return response

    def get_transactions(self, cobrand_session_token, user_session_token, params=None):  # nopep8
        url = self.config['BASE_URL'] + '/transactions'

        if params is None:
            now = datetime.now()
            two_months_ago = now - relativedelta(months=2)
            params = {
                'fromDate': two_months_ago.strftime('%Y-%m-%d'),
                'toDate': now.strftime('%Y-%m-%d'),
            }

        authorization = '{{cobSession={},userSession={}}}'.format(
            cobrand_session_token,
            user_session_token,
        )
        headers = {'Authorization': authorization}
        try:
            response = requests.get(url, params=params, headers=headers)
        except requests.exceptions.RequestException:
            message = 'Request url: {url}'.format(url=url)
            logging.error(message)
            raise

        utils.verify_json_response_or_raise_value_error(response)

        return response

    def register_user(self, cobrand_session_token, username, password, email):
        url = self.config['BASE_URL'] + '/user/register'
        register_param = {
            'user': {
                'loginName': username,
                'password': password,
                'email': email,
            }
        }
        data = {
            'registerParam': json.dumps(register_param),
        }
        authorization = '{{cobSession={}}}'.format(cobrand_session_token)
        headers = {'Authorization': authorization}
        try:
            response = requests.post(url, data=data, headers=headers)

        except requests.exceptions.RequestException:
            message = 'Request url: {url}'.format(url=url)
            logging.error(message)
            raise

        utils.verify_json_response_or_raise_value_error(response)

        return response

    def unregister_user(self, cobrand_session_token, user_session_token):
        url = self.config['BASE_URL'] + '/user/unregister'
        authorization = '{{cobSession={},userSession={}}}'.format(
            cobrand_session_token,
            user_session_token,
        )
        headers = {'Authorization': authorization}
        try:
            response = requests.delete(url, headers=headers)
        except requests.exceptions.RequestException:
            message = 'Request url: {url}'.format(url=url)
            logging.error(message)
            raise

        if response.status_code != 204:
            raise ValueError

        return response

    def get_fastlink_token(self, cobrand_session_token, user_session_token):
        url = self.config['BASE_URL'] + '/providers/token'
        authorization = '{{cobSession={},userSession={}}}'.format(
            cobrand_session_token,
            user_session_token,
        )
        headers = {'Authorization': authorization}
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException:
            message = 'Request url: {url}'.format(url=url)
            logging.error(message)
            raise

        utils.verify_json_response_or_raise_value_error(response)

        return response
