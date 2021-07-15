from src.handlers import proxy_handler
from src.utils import discord_webhook, cloudscraper_utils, address_api, info_generator
import config as CONFIG
import queue
import random
import time
import logging
import calendar
import threading
import os
from datetime import datetime
from faker import Faker
import pytz
from urllib3.exceptions import MaxRetryError
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected
from cloudscraper.exceptions import CloudflareCode1020

'''
SJS ENTER CONFIG
'''

SJS_RAFFLE_NAME = ''
SJS_VARIANTS = []
SJS_RAFFLE_URL = ''


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    account_queue = None
    with open(CONFIG.ROOT + '/output/accounts/sjs_accounts.txt', 'r') as file:
        accounts = list(file.read().split())
        account_queue = queue.Queue()
        [account_queue.put(a) for a in accounts]

    proxies = proxy_handler.get_proxy_list()

    area_codes = None
    with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
        area_codes = list(file.read().splitlines())

    return {
        'account_queue': account_queue,
        'proxies': proxies,
        'area_codes': area_codes
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set() and not shared_memory['account_queue'].empty():
        unparsed_account = shared_memory['account_queue'].get()

        try:
            result_from_parsing = [x.strip() for x in unparsed_account.split(':')]
            account = {
                'email': result_from_parsing[0],
                'password': result_from_parsing[1],
                'first_name': result_from_parsing[2],
                'last_name': result_from_parsing[3]
            }
        except AttributeError:
            account = unparsed_account

        if account_already_entered(account['email']):
            continue
        # each thread should have its own session
        session = cloudscraper_utils.create_scraper()

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

        # make registration request & verify
        successfully_entered = enter_raffle(session, account, proxy, shared_memory)

        if successfully_entered:
            email = account['email']
            write_account_to_file(email, proxy)
            discord_webhook.raffle_to_webhook(account, site="SJS", raffle=SJS_RAFFLE_NAME)
            print("[" + threading.currentThread().getName() + "] " + f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            session.close()

        else:
            shared_memory['account_queue'].put(account)
            print("Failed to register account. Adding account back to queue.")
            session.close()


def send_login_request(session, account, proxy):
    try:
        resp = session.get(
            url='https://www.slamjam.com/en_US/login',
            proxies=proxy,
            timeout=15
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled - " + str(e))
        return False

    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
        CSRF = soup.find('input', {'name': 'csrf_token'}).get('value')
        if CONFIG.DEBUG_MODE:
            print(CSRF)

    except Exception:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return False


    # populate data for registration request
    session.headers.update(
        {
            'referer': 'https://www.slamjam.com/en_US/login',
            'origin': 'https://www.slamjam.com',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
        }
    )

    login_data = {
        'loginEmail': account['email'],
        'loginPassword': account['password'],
        'timerInitilize': get_formatted_date_string(),
        'timerInitilizeClick': '',
        'countValidation': '0',
        'g-recaptcha-response': '',
        'getPreferences': '/on/demandware.store/Sites-SJS_Net_01-Site/en_US/Captcha-getPreferences',
        'verificationServer': '/on/demandware.store/Sites-SJS_Net_01-Site/en_US/Captcha-verificationServer',
        'enableRecaptcha': 'false',
        'csrf_token': CSRF
    }

    # perform registration request
    try:
        login_req = session.post(
            url='https://www.slamjam.com/on/demandware.store/Sites-SJS_Net_01-Site/en_US/Account-Login',
            data=login_data,
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled on Post- " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Account Creation Debug - ' + str(login_req.content))
        print('  Status - ' + str(login_req.status_code))

    if '"success": true' in str(login_req.content):
        success = True
    else:
        success = False

    return success


def enter_raffle(session, account, proxy, shared_memory):
    logged_in = send_login_request(session, account, proxy)
    if logged_in:
        if CONFIG.DEBUG_MODE:
            print('Logged in!')
    else:
        return False

    try:
        resp = session.get(
            url=SJS_RAFFLE_URL,
            proxies=proxy,
            timeout=15
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print(resp.content)
        print(resp.status_code)

    address = generate_address(shared_memory['area_codes'])
    if not address:
        return False

    time.sleep(random.randint(8, 15))

    data = {
        'variantID': random.choice(SJS_VARIANTS),
        'firstName': account['first_name'],
        'lastName': account['last_name'],
        'city': address['city'],
        'address1': address['address_1'],
        'address2': address['address_2'],
        'countryCode': 'US',
        'state': address['state'],
        'zipCode': address['postcode'],
        'phone': address['phone'],
        'prefix': '+1'
    }

    session.headers.update(
        {
            'Referer': SJS_RAFFLE_URL,
            'Origin': 'https://www.slamjam.com',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
        }
    )

    # perform registration request
    try:
        entry_res = session.post(
            url='https://www.slamjam.com/on/demandware.store/Sites-SJS_Net_01-Site/en_US/Raffle-AddRaffleProduct',
            data=data,
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled on Post- " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(entry_res.content))
        print('  Status - ' + str(entry_res.status_code))

    if '"error": false' in str(entry_res.content):
        success = True
    else:
        success = False

    return success


def account_already_entered(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/sjs/SJS_' + SJS_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'a+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return account in file.read()


def write_account_to_file(email, proxy):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/sjs/SJS_' + SJS_RAFFLE_NAME + '_entries.txt'
    proxy = proxy_handler.parse_into_default_form(proxy)

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'a+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ":" + proxy + '\n')


def get_formatted_date_string():
    tz_London = pytz.timezone('Europe/London')
    datetime_London = datetime.now(tz_London)
    fmt = '%Y %m %d %H:%M:%S'
    formatted_date = str(datetime_London.strftime(fmt))
    split = formatted_date.split()
    month = calendar.month_abbr[int(split[1])]
    day = calendar.day_abbr[calendar.weekday(int(split[0]), int(split[1]), int(split[2]))]
    formatted = day + ' ' + month + ' ' + split[2] + ' ' + split[3] + ' GMT ' + split[0]
    return formatted


def generate_address(area_codes):
    if not CONFIG.USE_FAKER:
        address = address_api.get_address('US')
        if not address:
            return False
        else:
            address['phone'] = random.choice(area_codes) + str(random.randint(1111111, 9999999))
    else:
        fake = Faker('en_US')

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'address_2': '',
            'city': fake.city(),
            'postcode': fake.zipcode(),
            'state': info_generator.convert_state(fake.state()),
            'phone': random.choice(area_codes) + str(random.randint(1111111, 9999999)),
        }

    return address

#
# def generate_csrf(proxy):
#     session = cloudscraper_utils.create_scraper()
#     r = session.post(
#         url='https://www.slamjam.com/on/demandware.store/Sites-SJS_Net_01-Site/en_US/CSRF-Generate',
#         proxies=proxy
#     )
#     print(r.content)
#     print(r.status_code)
#     token = r.json()
#     s = token['csrf']
#     return(s['token'])
#

def shutdown():
    print("\nThere are no more emails remaining to generate accounts! Shutting down.")
    logging.info("There are no more emails remaining to generate accounts! Shutting down.")
