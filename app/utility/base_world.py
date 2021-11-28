import binascii
import string
import re
import yaml
import logging
import subprocess
import distutils.version
from base64 import b64encode, b64decode
from datetime import datetime
from importlib import import_module
from random import randint, choice


class BaseWorld:
    """
    A collection of base static functions for service & object module usage
    """

    _app_configuration = dict()

    re_base64 = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', flags=re.DOTALL)
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def apply_config(name, config):
        BaseWorld._app_configuration[name] = config

    @staticmethod
    def clear_config():
        BaseWorld._app_configuration = {}

    @staticmethod
    def get_config(prop=None, name=None):
        name = name if name else 'main'
        if prop:
            return BaseWorld._app_configuration[name].get(prop)
        return BaseWorld._app_configuration[name]

    @staticmethod
    def set_config(name, prop, value):
        if value is not None:
            logging.debug('Configuration (%s) update, setting %s=%s' % (name, prop, value))
            BaseWorld._app_configuration[name][prop] = value

    @staticmethod
    def decode_bytes(s, strip_newlines=True):
        decoded = b64decode(s).decode('utf-8', errors='ignore')
        return decoded.replace('\r\n', '').replace('\n', '') if strip_newlines else decoded

    @staticmethod
    def encode_string(s):
        return str(b64encode(s.encode()), 'utf-8')

    @staticmethod
    def jitter(fraction):
        i = fraction.split('/')
        return randint(int(i[0]), int(i[1]))

    @staticmethod
    def create_logger(name):
        return logging.getLogger(name)

    @staticmethod
    def strip_yml(path):
        if path:
            with open(path, encoding='utf-8') as seed:
                return list(yaml.load_all(seed, Loader=yaml.FullLoader))
        return []

    @staticmethod
    def prepend_to_file(filename, line):
        with open(filename, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(line.rstrip('\r\n') + '\n' + content)

    @staticmethod
    def get_current_timestamp(date_format=TIME_FORMAT):
        return datetime.now().strftime(date_format)

    @staticmethod
    def get_timestamp_from_string(datetime_str, date_format=TIME_FORMAT):
        return datetime.strptime(datetime_str, date_format)

    @staticmethod
    async def load_module(module_type, module_info):
        module = import_module(module_info['module'])
        return getattr(module, module_type)(module_info)

    @staticmethod
    def generate_name(size=16):
        return ''.join(choice(string.ascii_lowercase) for _ in range(size))

    @staticmethod
    def generate_number(size=6):
        return randint((10 ** (size - 1)), ((10 ** size) - 1))

    @staticmethod
    def is_base64(s):
        try:
            b64decode(s, validate=True)
            return True
        except binascii.Error:
            return False

    @staticmethod
    def is_uuid4(s):
        if BaseWorld.re_base64.match(s):
            return True
        return False

    @staticmethod
    def template_matching(data, template):
        """
        注册一个计划
        :param data:
        :param template: 计划的类型
        :return bool:
        """
        loss_key = []
        for _ in template:
            if _ not in data:
                loss_key.append(_)
        if loss_key:
            raise Exception(f"缺少模板里面的字段： {loss_key}")

    @staticmethod
    def second2timestamp(second):
        return int(second) * 1000
