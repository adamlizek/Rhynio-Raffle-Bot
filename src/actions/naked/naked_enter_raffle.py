from src.handlers import captcha_handler, proxy_handler
from src.utils import discord_webhook, log_data, faker_generator, cloudscraper_utils
import config as CONFIG
import queue
import random
import time
import os
import json
import logging
import threading

from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected

'''
NAKED ENTER RAFFLE CONFIG
'''
NAKED_RAFFLE_URL = 'https://nakedcph.typeform.com/app/form/submit/'
NAKED_RAFFLE_WEBPAGE = ''
NAKED_RAFFLE_NAME = ''
NAKED_RAFFLE_FORM_ID = ''
NAKED_RAFFLE_CAPTCHA_TEXT = ''
NAKED_RAFFLE_COUNTRY = 'United States of America'
NAKED_RAFFLE_NEWSLETTER = 'Yes'
NAKED_ENTRY_DELAY = 30
NAKED_SHOW_FAILURE = False

NAKED_FIELD_ID_CAPTCHA = ''
NAKED_FIELD_ID_EMAIL = ''
NAKED_FIELD_ID_FIRSTNAME = ''
NAKED_FIELD_ID_LASTNAME = ''
NAKED_FIELD_ID_ADDRESS1 = ''
NAKED_FIELD_ID_ADDRESS2 = ''
NAKED_FIELD_ID_CITY = ''
NAKED_FIELD_ID_PHONE = ''
NAKED_FIELD_ID_ZIPCODE = ''
NAKED_FIELD_ID_COUNTRY = ''
NAKED_FIELD_ID_NEWSLETTER = ''

NAKED_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
NAKED_CAPTCHA_DATA_SITE_KEY = '6LeNqBUUAAAAAFbhC-CS22rwzkZjr_g4vMmqD_qo'
NAKED_CAPTCHA_URL = 'https://www.nakedcph.com/auth/view?op=register'

NAKED_ENTRY_LEVEL = 1 # Level 1 = Login, Navigate, Enter
                      # Level 2 = Navigate, Enter
                      # Level 3 = Enter


def init():
    logging.info("Beginning Raffle Entry...")
    print("Beginning Raffle Entry...\n")

    account_queue = None
    with open(CONFIG.ROOT + '/output/accounts/naked_accounts.txt', 'r') as file:
        accounts = list(file.read().split())
        account_queue = queue.Queue()
        [account_queue.put(a) for a in accounts]

    address_1 = None
    with open(CONFIG.ROOT + '/data/info/directions.txt', 'r') as file:
        address_1 = list(file.read().splitlines())

    address_2 = None
    with open(CONFIG.ROOT + '/data/info/addresses.txt', 'r') as file:
        address_2 = list(file.read().splitlines())

    address_3  = None
    with open(CONFIG.ROOT + '/data/info/streets.txt', 'r') as file:
        address_3 = list(file.read().splitlines())

    us_cities = None
    with open(CONFIG.ROOT + '/data/info/cities.txt', 'r') as file:
        us_cities = list(file.read().splitlines())

    dk_cities = None
    try:
        with open(CONFIG.ROOT + '/data/info/cities_dk.txt', 'r') as file:
            dk_cities = list(file.read().splitlines())
    except IOError:
        logging.info('[Error] - cities_dk.txt does not exist!')

    uk_cities = None
    try:
        with open(CONFIG.ROOT + '/data/info/cities_uk.txt', 'r') as file:
            uk_cities = list(file.read().splitlines())
    except IOError:
        logging.info('[Error] - cities_uk.txt does not exist!')

    fi_cities = None
    try:
        with open(CONFIG.ROOT + '/data/info/cities_FI.txt', 'r') as file:
            fi_cities = list(file.read().splitlines())
    except IOError:
        logging.info('[Error] - cities_FI.txt does not exist!')

    proxies = None
    with open(CONFIG.ROOT + '/data/proxies/proxy_lists.json', 'r') as json_file:
        data = json.load(json_file)

        list_id = 0
        while list_id < len(data['proxies']):
            if data['proxies'][list_id]['list_name'] == CONFIG.PROXY_LIST_NAME:
                break

        unformatted_proxy_list = data['proxies'][list_id]['proxies']
        proxies = proxy_handler.parse_into_request_format(unformatted_proxy_list)

    return {
        'account_queue': account_queue,
        'address_1': address_1,
        'address_2': address_2,
        'address_3': address_3,
        'proxies': proxies,
        'us_cities': us_cities,
        'dk_cities': dk_cities,
        'uk_cities': uk_cities,
        'fi_cities': fi_cities
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['account_queue'].empty():
        unparsed_account = shared_memory['account_queue'].get()

        result_from_parsing = [x.strip() for x in unparsed_account.split(':')]
        account = {
            'email': result_from_parsing[0],
            'password': result_from_parsing[1],
            'first_name': result_from_parsing[2],
            'last_name': result_from_parsing[3]
        }

        if account_already_entered(account['email']):
            continue

        # proxy = random.choice(proxies)
        try:
            proxy = random.choice(shared_memory['proxies'])
        except IndexError:
            print('All proxies have been used! Please enter more proxies')
            logging.info('All proxies have been used! Please enter more proxies')
            break

        try:
            shared_memory['proxies'].remove(proxy)
        except ValueError:
            if CONFIG.DEBUG_MODE:
                print('Proxy Already Removed')

        session = cloudscraper_utils.create_scraper()

        address = generate_address()
        successfully_entered = send_raffle_entry_request(account, session, proxy, address)

        if successfully_entered:
            write_account_to_file(account)
            discord_webhook.raffle_to_webhook(account, site="Naked", raffle=NAKED_RAFFLE_NAME)
            email = account['email']

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')

            if CONFIG.LOG_ENTRIES:
                log_data.log_entry_data(site="NAKED",
                                        raffle=NAKED_RAFFLE_NAME,
                                        email=email,
                                        proxy=proxy_handler.parse_into_default_form(proxy),
                                        delay=NAKED_ENTRY_DELAY,
                                        country=NAKED_RAFFLE_COUNTRY
                                        )
            session.close()

        else:
            shared_memory['account_queue'].put(unparsed_account)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            time.sleep(1)
            session.close()


def send_raffle_entry_request(account, session, proxy, address):
    if NAKED_ENTRY_LEVEL == 1:
        session, success = send_login_request(account, session, proxy)

        if success is False:
            print('Login Failed')
            return False
        else:
            if CONFIG.DEBUG_MODE:
                print('Login Success!')

    '''
    Navigation Request
    '''
    new_session = cloudscraper_utils.create_scraper()

    new_session.headers.update(
        {
            'referer': NAKED_RAFFLE_WEBPAGE,
        }
    )
    if NAKED_ENTRY_LEVEL == 1:
        new_session.headers.update(
            {
                'user-agent': session.headers['User-Agent'],
            }
        )
        new_session.cookies = session.cookies

    if NAKED_ENTRY_LEVEL < 3:
        try:
            navigation = new_session.get(
                url=NAKED_RAFFLE_WEBPAGE,
                proxies=proxy
            )
        except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
            print("Proxy Error Handled - " + str(e))
            print(proxy_handler.parse_into_default_form(proxy))
            return False

        try:
            navigation = new_session.post(
                url=NAKED_RAFFLE_WEBPAGE,
                proxies=proxy
            )
        except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
            print("Proxy Error Handled - " + str(e))
            print(proxy_handler.parse_into_default_form(proxy))
            return False

        if CONFIG.DEBUG_MODE:
            print('Navigation Debug - ' + str(navigation.content))
            print('  Status - ' + str(navigation.status_code))

    token_headers = {
        'accept': 'application/json',
        'origin': 'https://nakedcph.typeform.com',
        'referer': 'https://nakedcph.typeform.com/to/' + NAKED_RAFFLE_FORM_ID,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': NAKED_USER_AGENT
    }

    '''
    Get Typeform
    '''

    try:
        get_typeform = new_session.get(
            url="https://nakedcph.typeform.com/to/" + NAKED_RAFFLE_FORM_ID,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Get Typeform Debug - ' + str(get_typeform.content))
        print('  Status - ' + str(get_typeform.status_code))
        print('  Cookies - ' + str(session.cookies))

    try:
        access_token = new_session.get(
            url="https://nakedcph.typeform.com/app/form/result/token/" + NAKED_RAFFLE_FORM_ID + '/default',
            proxies=proxy,
            headers=token_headers,
            json={"key": "value"})
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    json_data = json.loads(access_token.text)
    token = json_data["token"]
    landed_at = json_data["landed_at"]

    if CONFIG.DEBUG_MODE:
        print('Token - ' + token)
        print('Landed At - ' + landed_at)

    if CONFIG.DEBUG_MODE:
        print('Waiting for ' + str(NAKED_ENTRY_DELAY))

    time.sleep(int(NAKED_ENTRY_DELAY))

    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json; charset=UTF-8',
        'origin': 'https://nakedcph.typeform.com',
        'referer': 'https://nakedcph.typeform.com/to/' + NAKED_RAFFLE_FORM_ID,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': NAKED_USER_AGENT,
    }

    formatted_country = NAKED_RAFFLE_COUNTRY
    if formatted_country == 'United States':
        formatted_country = 'United States of America'

    data = {
        "signature": token,
        "form_id": NAKED_RAFFLE_FORM_ID,
        "landed_at": int(landed_at),
        "answers": [
            {
                "field": {
                    "id": NAKED_FIELD_ID_EMAIL,
                    "type": "email"
                },
                "type": "email",
                "email": account['email']
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_FIRSTNAME,
                    "type": "short_text"
                },
                "type": "text",
                "text": account['first_name']
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_LASTNAME,
                    "type": "short_text"
                },
                "type": "text",
                "text": account['last_name']
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_COUNTRY,
                    "type": "dropdown"
                },
                "type": "text",
                "text": formatted_country
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_ADDRESS1,
                    "type": "short_text"
                },
                "type": "text",
                "text": address["address_1"]
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_CITY,
                    "type": "short_text"
                },
                "type": "text",
                "text": address["city"]
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_ZIPCODE,
                    "type": "short_text"
                },
                "type": "text",
                "text": address["zip"]
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_PHONE,
                    "type": "phone_number"
                },
                "type": "phone_number",
                "phone_number": address["phone_number"]
            },
            {
                "field": {
                    "id": NAKED_FIELD_ID_NEWSLETTER,
                    "type": "dropdown"
                },
                "type": "text",
                "text": NAKED_RAFFLE_NEWSLETTER
            }
        ]
    }

    #print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in data.items()) + "}")

    url = NAKED_RAFFLE_URL + NAKED_RAFFLE_FORM_ID

    try:
        response = new_session.post(url=url,
                                    json=data,
                                    headers=headers,
                                    proxies=proxy)
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.content))
        print('  Status - ' + str(response.status_code))

    success = response.ok
    return success


def send_login_request(account, session, proxy):
    # populate data for registration request
    '''
    Initial Get Request
    '''

    try:
        initial = session.get(
            url='https://www.nakedcph.com/en/auth/view',
            proxies=proxy,
            timeout=10
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError, Exception) as e:
        print("Proxy Error Handled - " + str(e))
        print(proxy_handler.parse_into_default_form(proxy))
        return session, False

    if CONFIG.DEBUG_MODE:
        print('[1] Login Debug - ' + str(initial.content))
        print('  Status - ' + str(initial.status_code))

    try:
        ANTI_CSRF_TOKEN = session.cookies.get_dict()['AntiCsrfToken']

    except KeyError:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return session, False

    '''
    Login Post Request
    '''

    # populate data for registration request
    session.headers.update(
        {
            'referer': 'https://www.nakedcph.com/en/auth/view',
            'origin': 'https://www.nakedcph.com',
            'sec-fetch-mode': 'cors',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-fetch-site': 'same-origin',
            'x-anticsrftoken': ANTI_CSRF_TOKEN,
            'x-requested-with': 'XMLHttpRequest',
        }
    )

    login_data = {
        '_AntiCsrfToken': ANTI_CSRF_TOKEN,
        'action': 'login',
        'email': account['email'],
        'g-recaptcha-response': captcha_handler.handle_captcha(NAKED_CAPTCHA_URL,
                                                               NAKED_CAPTCHA_DATA_SITE_KEY),
        'password': account['password']
    }

    # perform login request
    try:
        login_request = session.post(
            url='https://www.nakedcph.com/en/auth/submit',
            data=login_data,
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception):
        print("Proxy Error Handled")
        return session, False

    if login_request.status_code == 500:
        if "ReCaptchaFailed" in login_request.text:
            return session, False

    if CONFIG.DEBUG_MODE:
        print('[2] Account Login Debug - ' + str(login_request.content))
        print('  Status - ' + str(login_request.status_code))

    if login_request.text == '{"Response":{"Success":true,"Action":"Login"},"StatusCode":0,"Status":"OK"}':
        success = True
    else:
        success = False

    return session, success


def account_already_entered(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Naked_' + NAKED_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return account in file.read()


def write_account_to_file(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Naked_' + NAKED_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(account['email'] + '\n')


def generate_address():
    country = NAKED_RAFFLE_COUNTRY

    if NAKED_RAFFLE_COUNTRY == 'Random':
        country = random.choice(['United States', 'Denmark',
                                 'United Kingdom', 'Germany',
                                 'France', 'Spain', 'Portugal', 'Romania'])

    address_info = faker_generator.generate_naked_address(country)

    return address_info


def shutdown():
    discord_webhook.raffle_entry_complete("Naked", NAKED_RAFFLE_NAME)
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")
