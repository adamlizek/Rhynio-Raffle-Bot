import requests
import time
import re
import config
from requests import ConnectionError


def handle_captcha(captcha_url, captcha_data_site_key, action=None, invisible=False, hcaptcha=False):
    sent = False
    while not sent:
        response = send_to_2Captcha(captcha_url, captcha_data_site_key, action, invisible, hcaptcha)

        if config.DEBUG_MODE:
            print(response)

        if 'OK' in str(response):
            sent = True
        else:
            time.sleep(1)

    return receive_key_from_2Captcha(response)


def send_to_2Captcha(captcha_url, captcha_data_site_key, action=None, invisible=False, hcaptcha=False):
    if hcaptcha:
        captcha_string = '&method=hcaptcha&sitekey='
    else:
        captcha_string = '&method=userrecaptcha&googlekey='

    sent = False
    while not sent:
        try:
            if action is None:
                if invisible:
                    url = str(config.TWO_CAPTCHA_URL_IN + '?key=' +
                              config.two_captcha_api_key + '&method=userrecaptcha&googlekey=' +
                              captcha_data_site_key + '&pageurl=' + captcha_url + '&invisible=1')
                else:
                    url = str(config.TWO_CAPTCHA_URL_IN + '?key=' +
                              config.two_captcha_api_key + captcha_string +
                              captcha_data_site_key + '&pageurl=' + captcha_url)
            else:
                url = str(config.TWO_CAPTCHA_URL_IN + '?key=' +
                          config.two_captcha_api_key + '&method=userrecaptcha&version=v3&action=' + action +
                          '&min_score=0.3&' + 'googlekey=' + captcha_data_site_key + '&pageurl=' + captcha_url)

            response = requests.get(url=url)
            sent = True

        # occurs if 2 captcha denies our request due to too many requests
        except ConnectionError:
            time.sleep(5)
            continue

    return response.content


def receive_key_from_2Captcha(response):
    response = str(response)
    response_id = re.sub("[^0-9]", "", response)

    received = False
    while not received:
        # request solved captcha key from 2Captcha
        try:
            url = str(config.TWO_CAPTCHA_URL_OUT + '?key=' +
                      config.two_captcha_api_key + '&action=get&id=' + response_id)

            response = requests.get(url=url)

        # occurs if 2 captcha denies our request due to too many requests
        except ConnectionError:
            time.sleep(5)
            continue

        response_text = str(response.content)

        # in the event of a bricked captcha, the quickest thing to do to solve
        # is to just return an invalid captcha token (ie: 'error') and
        # cause the request to fail. The account will still be added
        # back to the queue
        if 'ERROR_CAPTCHA_UNSOLVABLE' in response_text:
            return 'error'

        # checks success, retry if failure
        response_text = response_text[2:4]
        if response_text == 'OK':
            received = True
        else:
            time.sleep(3)
            continue

    captcha_key = str(response.content)[5:-1]
    return captcha_key


def handle_image_captcha(base64_image):
    sent = False
    while not sent:
        response = send_image_to_2Captcha(base64_image)

        if config.DEBUG_MODE:
            print(response)

        if 'OK' in str(response):
            sent = True
        else:
            time.sleep(1)

    return receive_key_from_2Captcha(response)


def send_image_to_2Captcha(base64_image):
    sent = False
    while not sent:
        try:
            url = config.TWO_CAPTCHA_URL_IN
            data = {'key': config.two_captcha_api_key, 'body': base64_image, 'method': 'base64'}
            response = requests.post(url, data=data)
            sent = True

        # occurs if 2 captcha denies our request due to too many requests
        except ConnectionError:
            time.sleep(5)
            continue

    return response.content
