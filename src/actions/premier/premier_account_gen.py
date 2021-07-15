from src.handlers import proxy_handler, captcha_handler, email_handler
from src.utils import info_generator, discord_webhook, cloudscraper_utils
import config as CONFIG
import portalocker
from faker import Faker
import random
import time
import logging
import threading
import os
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected
from bs4 import BeautifulSoup


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

        account = {
            'email': email,
            'password': info_generator.get_random_password(),
            'first_name': first_name,
            'last_name': last_name
        }

        # make registration request & verify
        proxy = random.choice(shared_memory['proxies'])

        successfully_registered = send_registration_requests(account, proxy)

        if successfully_registered:
            write_account_to_file(account)
            discord_webhook.account_to_webhook(account, site='Premier')
            print("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            time.sleep(2)

        else:
            shared_memory['email_queue'].put(unparsed_email)
            print("Failed to register account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to register account. Adding account back to queue.")
            time.sleep(2)


def send_registration_requests(account, proxy):
    scraper = cloudscraper_utils.create_scraper()

    try:
        resp = scraper.get(
            url='https://thepremierstore.com/account/register',
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Initial Request Debug - ' + str(resp.content))
        print('  Status - ' + str(resp.status_code))
        print('  Cookies - ' + str(scraper.cookies))

    # populate data for registration request
    scraper.headers.update(
        {
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://thepremierstore.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'referer': 'https://thepremierstore.com/account/register',
            'accept-encoding': 'gzip, deflate, br'
        }
    )

    registration_data = {
        'form_type': 'create_customer',
        'utf8': '✓',
        'customer[email]': account['email'],
        'customer[first_name]': account['first_name'],
        'customer[last_name]': account['last_name'],
        'customer[password]': account['password'],
        'customer[accepts_marketing]': 'false',
    }

    # perform registration request
    try:
        registration_request = scraper.post(
            url='https://thepremierstore.com/account',
            data=registration_data,
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception):
        print("Proxy Error Handled")
        return False

    if CONFIG.DEBUG_MODE:
        print('Account Creation Debug - ' + str(registration_request.content))
        print('  Status - ' + str(registration_request.status_code))
        print('  Cookies - ' + str(scraper.cookies))

    captcha_token = captcha_handler.handle_captcha('https://thepremierstore.com/challenge', '6LeoeSkTAAAAAA9rkZs5oS82l69OEYjKRZAiKdaF')
    if len(captcha_token) < 10:
        return False

    try:
        soup = BeautifulSoup(registration_request.text, 'html.parser')
        authenticity_token = soup.find('input', {'name': 'authenticity_token'}).get('value')
        if CONFIG.DEBUG_MODE:
            print(authenticity_token)
    except Exception:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return False

    captcha_data = {
        'authenticity_token': authenticity_token,
        'g-recaptcha-response': captcha_token
    }

    scraper.headers.update({
        'referer': 'https://thepremierstore.com/challenge'
    })

    # perform captcha request
    try:
        captcha_request = scraper.post(
            url='https://thepremierstore.com/account',
            data=captcha_data,
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception):
        print("Proxy Error Handled")
        return False

    if CONFIG.DEBUG_MODE:
        print('Captcha Debug - ' + str(captcha_request.content))
        print('  Status - ' + str(captcha_request.status_code))
        print('  Cookies - ' + str(scraper.cookies))

    try:
        verification_request = scraper.get(
            url='https://thepremierstore.com/account',
            proxies=proxy,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception):
        print("Proxy Error Handled")
        return False

    if CONFIG.DEBUG_MODE:
        print('Verification Status - ' + str(verification_request.status_code))
        print('  Text - ' + str(verification_request.text))
        print('  Cookies - ' + str(scraper.cookies))

    if account['first_name'] in verification_request.text:
        success = True
    else:
        success = False

    return success


def email_already_registered(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/accounts/premier_accounts.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/accounts/premier_accounts.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        portalocker.lock(file, portalocker.LOCK_EX)
        file.write(account['email'] + ":" + account['password'] +
        ":" + account['first_name'] + ":" + account['last_name'] + "\n")


def shutdown():
    print("\nThere are no more emails remaining to generate accounts! Shutting down.")
    logging.info("There are no more emails remaining to generate accounts! Shutting down.")
