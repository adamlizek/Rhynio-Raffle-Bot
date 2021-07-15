from src.handlers import proxy_handler, captcha_handler, email_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils, faker_generator
import config as CONFIG
import random
import time
import logging
import string
import os
from pathlib import Path
import threading
from faker import Faker
from random import randint
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected
from requests_toolbelt import MultipartEncoder

'''
DSML ENTRY CONFIG
'''
DSML_RAFFLE_WEBPAGE = ''
DSML_RAFFLE_URL = ''
DSML_RAFFLE_NAME = ''
DSML_COUNTRY_NAME = ''
DSML_SIZE_ID = ''
DSML_REFERER_HEADER = ''
DSML_FORMSTACK_URL = ''

DSML_NAME_ID = ''
DSML_EMAIL_ID = ''
DSML_PHONE_ID = ''
DSML_ADDRESS1_ID = ''
DSML_COLOR_ID = ''
DSML_COLOR_VALUE = ''
DSML_COUNTRY_ID = ''
DSML_ZIP_ID = ''
DSML_FORM_ID = ''
DSML_VIEWKEY = ''
DSML_VIEWPARAM = ''
DSML_HIDDEN_FIELDS = ''

DSML_PLUSTRICK_ENABLED = False
DSML_GMAIL = ''

DSML_CATCHALL_ENABLED = False
DSML_CATCHALL = ''

DSML_DATA_SITEKEY = '6LetKEIUAAAAAPk-uUXqq9E82MG3e40OMt_74gjS'


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_queue = email_handler.get_email_queue()
    proxies = proxy_handler.get_proxy_list()

    sizes = ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 11.5", "US 12", "US 13"]

    return {
        'email_queue': email_queue,
        'proxies': proxies,
        'sizes': sizes
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        fake = Faker('en_US')

        name = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name()
        }

        if DSML_PLUSTRICK_ENABLED:
            result_from_parsing = [x.strip() for x in DSML_GMAIL.split('@')]
            email_split = result_from_parsing[0]
            email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"
        elif DSML_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(randint(10, 99)) + '@' + DSML_CATCHALL
        else:
            unparsed_email = shared_memory['email_queue'].get()
            email = unparsed_email.get_email()
            if unparsed_email.nameEnabled():
                name = {
                    'first_name': unparsed_email.get_first_name(),
                    'last_name': unparsed_email.get_last_name()
                }

        if email_already_entered(email):
            continue

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

        # make registration request & verify
        successfully_entered = send_entry_requests(email, name, session, proxy, shared_memory)

        if successfully_entered:
            write_account_to_file(email, proxy)
            discord_webhook.raffle_to_webhook(email, site="DSML Entry", raffle=DSML_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info(
                "[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')

            log_data.log_entry_data(site="DSML",
                                    raffle=DSML_RAFFLE_NAME,
                                    email=email,
                                    proxy=proxy_handler.parse_into_default_form(proxy),
                                    country='US',
                                    delay='Captcha'
                                    )

            session.close()

        else:
            if not DSML_CATCHALL_ENABLED and not DSML_PLUSTRICK_ENABLED:
                shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            session.close()
            time.sleep(1)


def send_entry_requests(email, name, scraper, proxy, shared_memory):
    try:
        resp = scraper.get(
            url=DSML_RAFFLE_URL,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    scraper.headers.update(
        {
            'referer': 'https://london.doverstreetmarket.com/',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site',
        }
    )

    try:
        resp = scraper.get(
            url=DSML_FORMSTACK_URL,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    captcha_token = captcha_handler.handle_captcha(DSML_RAFFLE_URL, DSML_DATA_SITEKEY, invisible=True)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False

    size = random.choice(shared_memory['sizes'])

    address = generate_address()

    def get_random_string(length):
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    files = {
        'form': DSML_FORM_ID,
        'viewkey': DSML_VIEWKEY,
        'password': '',
        'hidden_fields': DSML_HIDDEN_FIELDS,
        'incomplete': '',
        'incomplete_password': '',
        'referrer': 'https://london.doverstreetmarket.com/',
        'referrer_type': 'js',
        '_submit': '1',
        'style_version': '3',
        'viewparam': DSML_VIEWPARAM,
        DSML_NAME_ID: name['first_name'] + ' ' + name['last_name'],
        DSML_PHONE_ID: address['phone'],
        DSML_EMAIL_ID: email,
        DSML_COLOR_ID: DSML_COLOR_VALUE,
        DSML_SIZE_ID: size,
        DSML_ADDRESS1_ID: address['address_1'],
        DSML_COUNTRY_ID: DSML_COUNTRY_NAME,
        DSML_ZIP_ID: address['zip'],
        'g-recaptcha-response': captcha_token,
        'nonce': get_random_string(16),
    }

    m = MultipartEncoder(files, boundary=generate_boundary())

    scraper.headers.update(
        {
            'content-type': m.content_type,
            'origin': 'https://london.doverstreetmarket.com',
            'referer': 'https://london.doverstreetmarket.com/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }
    )

    try:
        response = scraper.post(
            url='https://doverstreetmarketinternational.formstack.com/forms/index.php',
            data=m.to_string(),
            allow_redirects=False,
            proxies=proxy,
            timeout=45
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.content))
        print('  Status - ' + str(response.status_code))
        print('  Cookies - ' + str(scraper.cookies))

    if str(scraper.get_redirect_target(
            response)) == 'https://london.doverstreetmarket.com/new-items/raffl-e/thank-you':
        success = True
    elif "The form was submitted successfully." in str(response.content):
        success = True
    else:
        success = False

    return success

def generate_address():
    fake = faker_generator.generate_country_faker(DSML_COUNTRY_NAME)

    phone_number = faker_generator.generate_yme_phone_number(DSML_COUNTRY_NAME)

    address = {
        'address_1': fake.street_address(),
        'zip': fake.postcode(),
        'phone': phone_number,
    }

    return address


def generate_boundary(size=16):
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits +
                                 string.ascii_lowercase, k=size))

    prefix = '------WebKitFormBoundary'

    return prefix + res


def email_already_entered(email):
    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/DSML_' + DSML_RAFFLE_NAME + '.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/DSML_' + DSML_RAFFLE_NAME + '.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="DSML", raffle=DSML_RAFFLE_NAME)
