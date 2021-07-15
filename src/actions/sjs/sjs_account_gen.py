from src.handlers import proxy_handler, email_handler
from src.utils import info_generator, discord_webhook, cloudscraper_utils
import config as CONFIG
import portalocker
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
SJS ACCOUNT GEN CONFIG
'''
SJS_CUSTOM_PASSWORD_ENABLED = False
SJS_CUSTOM_PASSWORD = ''



def init():
    print("Beginning Account Generation...\n")
    logging.info("Beginning Account Generation...")

    email_queue = email_handler.get_email_queue()
    proxies = proxy_handler.get_proxy_list()

    return {
        'email_queue': email_queue,
        'proxies': proxies
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        unparsed_email = shared_memory['email_queue'].get()
        email = unparsed_email.get_email()

        if email_already_registered(email):
            continue

        fake = Faker()

        if unparsed_email.nameEnabled():
            first_name = unparsed_email.get_first_name()
            last_name = unparsed_email.get_last_name()
        else:
            first_name = fake.first_name()
            last_name = fake.last_name()

        # each thread should have its own session
        session = cloudscraper_utils.create_scraper()

        account = {
            'email': email,
            'password': info_generator.get_random_password() + random.choice(['$', '%', '&']),
            'first_name': first_name,
            'last_name': last_name,
            'proxy': random.choice(shared_memory['proxies'])
        }
        if SJS_CUSTOM_PASSWORD_ENABLED:
            account['password'] = SJS_CUSTOM_PASSWORD

        # make registration request & verify
        successfully_registered = send_registration_requests(session, account)

        if successfully_registered:
            write_account_to_file(account)
            discord_webhook.account_to_webhook(account, site='SJS')
            print("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            session.close()

        else:
            shared_memory['email_queue'].put(unparsed_email)
            print("Failed to register account. Adding account back to queue.")
            #logging.info("[" + threading.currentThread().getName() + "] " + "Failed to register account. Adding account back to queue.")
            session.close()


def send_registration_requests(session, account):
    proxy = account['proxy']

    try:
        resp = session.get(
            url='https://www.slamjam.com/en_US/login?action=register',
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
        print(resp.content)
        return False

    # populate data for registration request
    session.headers.update(
        {
            'referer': 'https://www.slamjam.com/en_US/login?action=register',
            'origin': 'https://www.slamjam.com',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
        }
    )

    registration_data = {
        'dwfrm_profile_customer_title': 'Mr',
        'dwfrm_profile_customer_firstname': account['first_name'],
        'dwfrm_profile_customer_lastname': account['last_name'],
        'dwfrm_profile_customer_birthday': str(random.randint(1, 28)) + '/0' + str(random.randint(1, 9)) + '/' + str(random.randint(1985, 2002)),
        'dwfrm_profile_customer_email': account['email'],
        'dwfrm_profile_customer_emailconfirm': account['email'],
        'dwfrm_profile_login_password': account['password'],
        'dwfrm_profile_login_passwordconfirm': account['password'],
        'checkPrivacy': 'true',
        'directMarketing': 'true',
        'profiling': 'true',
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
        registration_request = session.post(
            url='https://www.slamjam.com/on/demandware.store/Sites-SJS_Net_01-Site/en_US/Account-SubmitRegistration?rurl=1',
            data=registration_data,
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled on Post- " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Account Creation Debug - ' + str(registration_request.content))
        print('  Status - ' + str(registration_request.status_code))

    if account['email'] in str(registration_request.content) and account['last_name'] in str(registration_request.content):
        success = True
    else:
        success = False

    return success


def email_already_registered(email):
    FILE_PATH = CONFIG.ROOT + '/output/accounts/sjs_accounts.txt'

    if not os.path.exists(FILE_PATH):
        file = open(FILE_PATH, 'w+')
        file.close()

    with open(FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(account):
    FILE_PATH = CONFIG.ROOT + '/output/accounts/sjs_accounts.txt'

    if not os.path.exists(FILE_PATH):
        file = open(FILE_PATH, 'w+')
        file.close()

    with open(FILE_PATH, 'a+') as file:
        portalocker.lock(file, portalocker.LOCK_EX)
        file.write(account['email'] + ":" + account['password'] +
        ":" + account['first_name'] + ":" + account['last_name'] + "\n")


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


def shutdown():
    print("\nThere are no more emails remaining to generate accounts! Shutting down.")
    logging.info("There are no more emails remaining to generate accounts! Shutting down.")
