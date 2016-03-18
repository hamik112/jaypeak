import os

from .client import Client
from .schemas import ErrorResponseMixin, FastlinkTokenResponseMixin, \
    LoginCobrandResponseMixin, LoginUserResponseMixin, \
    RegisterUserResponseMixin


class SandboxConfig(object):
    COBRAND_NAME = 'restserver'
    BASE_URL = 'https://developer.api.yodlee.com/ysl/{}/v1'.format(
        COBRAND_NAME)
    COBRAND_USERNAME = 'sbCobmassover'
    COBRAND_PASSWORD = '23f6f69b-d434-49b7-aec1-21a04e7da19e'
    FASTLINK_URL = 'https://node.developer.yodlee.com/authenticate/restserver/'


class ProductionConfig(object):
    COBRAND_NAME = 'quickstart6'
    BASE_URL = 'https://quickstart.api.yodlee.com/ysl/{}/v1'.format(
        COBRAND_NAME)
    COBRAND_USERNAME = 'quickstart6'
    COBRAND_PASSWORD = os.getenv('YODLEE_COBRAND_PASSWORD')
    FASTLINK_URL = 'https://quickstartnode.yodleeinteractive.com/authenticate/{}/?channelAppName=quickstart'.format(
        COBRAND_NAME)
