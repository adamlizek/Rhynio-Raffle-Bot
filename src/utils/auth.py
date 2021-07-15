import config
import json
from pathlib import Path
from getmac import get_mac_address as gma
import requests


def update_token(token):
    if config.CAPTCHA_SOLVER == config.CaptchaSolver.TWO_CAPTCHA:
        captcha_solver = "2CAPTCHA"
    elif config.CAPTCHA_SOLVER == config.CaptchaSolver.CAPMONSTER_CAPTCHA:
        captcha_solver = "CAPMONSTER"
    else:
        captcha_solver = "ANTICAPTCHA"

    user_info = {
        "ACCESS_KEY": config.license_key,
        "TWO_CAPTCHA_API_KEY": config.two_captcha_api_key,
        "ANTI_CAPTCHA_API_KEY": config.anticaptcha_api_key,
        "CAPTCHA_SOLVER": captcha_solver,
        "WEBHOOK": config.global_webhook,
        "TOKEN": token
    }
    with open(str(Path(config.ROOT + '/data/user/saved_info.json')), 'w') as f:
        json.dump(user_info, f, indent=2)

    config.token = token


def try_to_get_new_valid_token():
    data = {
        'key': config.license_key,
        'mac': gma()
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        res = requests.post(
            url=config.auth_api_endpoint + '/gettoken',
            json=data,
            headers=headers
        )
    except Exception as e:
        print(e)
        return False

    if config.DEBUG_MODE:
        print(res.content)
        print(res.status_code)

    if res.status_code == 200:
        json_res = res.json()
        update_token(json_res['token'])
        return True
    else:
        return False


def valid_access_key():
    if config.token == '':
        return try_to_get_new_valid_token()

    data = {
        'token': config.token,
        'mac': gma()
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        res = requests.post(
            url=config.auth_api_endpoint + '/checklicense',
            json=data,
            headers=headers
        )
    except Exception as e:
        print(e)
        return False

    if config.DEBUG_MODE:
        print(res.content)
        print(res.status_code)

    if res.status_code == 200:
        return True
    else:
        update_token('')
        return False
