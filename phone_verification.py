from cffi.backend_ctypes import unicode
import hashlib
import json
import requests
import time
import config


REDSMS_LOGIN = config.REDSMS_LOGIN
ts = unicode(time.time())
REDSMS_KEY = config.REDSMS_KEY
secret = hashlib.md5((ts + REDSMS_KEY).encode()).hexdigest()

auth_headers = {
    "login": REDSMS_LOGIN,
    "ts": ts,
    "secret": secret,
    "Content-type": "application/json",
}


def _generate_code():
    """Генерация случайного кода заданной длины"""
    import random

    return "".join(random.choice("0123456789") for i in range(4))


def _init_call(phone, code):
    """Инициализация звонка"""
    data = {"route": "fcall", "to": phone, "text": code}

    r = requests.post(
        "https://cp.redsms.ru/api/message", headers=auth_headers, data=json.dumps(data)
    )

    return r.json()


def _is_delivered(uuid):
    res = requests.get(f'https://cp.redsms.ru/api/message/{uuid}', headers=auth_headers).json()
    return res['success'] and res['item']['status'] == 'delivered'


def verify_phone(phone):
    """Верефикация номера телефона"""

    while True:
        code = _generate_code()
        r = _init_call(phone, code)
        
        if r['success']:
            is_deliv = _is_delivered(r['items'][0]['uuid'])
            if is_deliv:
                break



    return _init_call(phone, code)

