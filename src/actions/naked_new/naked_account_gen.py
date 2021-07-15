from src.handlers import captcha_handler, proxy_handler, email_handler
from src.utils import info_generator, discord_webhook, cloudscraper_utils
import config as CONFIG
import portalocker
import random
import time
import logging
import threading
import os
from faker import Faker
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected
from cloudscraper.exceptions import CloudflareCode1020

'''
NAKED ACCOUNT GEN CONFIG
'''
NAKED_CAPTCHA_DATA_SITE_KEY = '6LeNqBUUAAAAAFbhC-CS22rwzkZjr_g4vMmqD_qo'
NAKED_CAPTCHA_URL = 'https://www.nakedcph.com/auth/view?op=register'
NAKED_CUSTOM_PASSWORD_ENABLED = False
NAKED_CUSTOM_PASSWORD = ''


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
            'password': info_generator.get_random_password(),
            'first_name': first_name,
            'last_name': last_name,
            'proxy': random.choice(shared_memory['proxies'])
        }
        if NAKED_CUSTOM_PASSWORD_ENABLED:
            account['password'] = NAKED_CUSTOM_PASSWORD

        # make registration request & verify
        try:
            successfully_registered = send_registration_requests(session, account)
        except Exception as e:
            if CONFIG.DEBUG_MODE:
                print(e)
            logging.info("[" + threading.currentThread().getName() + "] " + f'Error generating {email} due to proxy CF issues.')
            successfully_registered = False

        if successfully_registered:
            write_account_to_file(account)
            discord_webhook.account_to_webhook(account, site='Naked')
            print("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            session.close()

        else:
            shared_memory['email_queue'].put(unparsed_email)
            print("Failed to register account. Adding account back to queue.")
            session.close()


def send_registration_requests(session, account):
    proxy = account['proxy']
    session.proxies = proxy

    try:
        session.get(
            url='https://www.nakedcph.com',
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled - " + str(e))
        return False

    try:
        ANTI_CSRF_TOKEN = session.cookies.get_dict()['AntiCsrfToken']

    except KeyError:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return False

    # populate data for registration request
    session.headers.update(
        {
            'Referer': 'https://www.nakedcph.com/en/auth/view?op=register',
            'Origin': 'https://www.nakedcph.com',
            'X-Anticsrftoken': ANTI_CSRF_TOKEN,
            'X-Requested-With': 'XMLHttpRequest',
        }
    )

    registration_data = {
        '_AntiCsrfToken': ANTI_CSRF_TOKEN,
        'action': 'register',
        'email': account['email'],
        'firstName': account['first_name'],
        'g-recaptcha-response': captcha_handler.handle_captcha(
            NAKED_CAPTCHA_URL,
            NAKED_CAPTCHA_DATA_SITE_KEY
        ),
        'password': account['password'],
        'termsAccepted': 'true'
    }

    # perform registration request
    try:
        registration_request = session.post(
            url='https://www.nakedcph.com/en/auth/submit',
            data=registration_data,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, CloudflareCode1020) as e:
        if CONFIG.DEBUG_MODE:
            print("Proxy Error Handled on Post- " + str(e))
        return False

    if registration_request.status_code == 500:
        if "ReCaptchaFailed" in registration_request.text:
            return False
        else:
            print(account['email'] + ' has already been created! Password is Wrong!')
            return True

    if CONFIG.DEBUG_MODE:
        print('Account Creation Debug - ' + str(registration_request.content))
        print('  Status - ' + str(registration_request.status_code))

    if registration_request.text == '{"Response":{"Success":true,"Action":"Register"},"StatusCode":0,"Status":"OK"}':
        success = True
    else:
        success = False

    return success


def email_already_registered(email):
    FILE_PATH = CONFIG.ROOT + '/output/accounts/naked_accounts.txt'

    if not os.path.exists(FILE_PATH):
        file = open(FILE_PATH, 'w+')
        file.close()

    with open(FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(account):
    FILE_PATH = CONFIG.ROOT + '/output/accounts/naked_accounts.txt'

    if not os.path.exists(FILE_PATH):
        file = open(FILE_PATH, 'w+')
        file.close()

    with open(FILE_PATH, 'a+') as file:
        portalocker.lock(file, portalocker.LOCK_EX)
        file.write(account['email'] + ":" + account['password'] + 
        ":" + account['first_name'] + ":" + account['last_name'] + "\n")


def shutdown():
    print("\nThere are no more emails remaining to generate accounts! Shutting down.")
    logging.info("There are no more emails remaining to generate accounts! Shutting down.")

