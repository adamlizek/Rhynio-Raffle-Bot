from src.handlers import proxy_handler, captcha_handler, email_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils, address_api, info_generator
import config as CONFIG
import queue
import random
import time
import logging
import json
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
DSM ENTRY CONFIG
'''
DSM_RAFFLE_WEBPAGE = ''
DSM_FORMSTACK_URL = ''
DSM_RAFFLE_URL = ''
DSM_RAFFLE_NAME = ''
DSM_SIZE_ID = ''
DSM_REFERER_HEADER = ''
DSM_SUCCESS_URL = ''
DSM_NAME_ID = ''
DSM_EMAIL_ID = ''
DSM_PHONE_ID = ''
DSM_ADDRESS1_ID = ''
DSM_STATE_ID = ''
DSM_ZIP_ID = ''
DSM_MAILING_ID = ''
DSM_FORM_ID = ''
DSM_VIEWKEY = ''
DSM_VIEWPARAM = ''

DSM_HIDDEN_FIELDS = ''

DSM_COLOR_ID = ''
DSM_COLOR = ''

DSM_QUESTION_ID = ''

DSM_PLUSTRICK_ENABLED = False
DSM_GMAIL = ''

DSM_CATCHALL_ENABLED = False
DSM_CATCHALL = ''

DSM_DATA_SITEKEY = '6LetKEIUAAAAAPk-uUXqq9E82MG3e40OMt_74gjS'


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_queue = email_handler.get_email_queue()
    proxies = proxy_handler.get_proxy_list()

    sizes = ["US 5.5", "US 6", "US 6.5", "US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 11.5", "US 12", "US 12.5", "US 13"]

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

        if DSM_PLUSTRICK_ENABLED:
            result_from_parsing = [x.strip() for x in DSM_GMAIL.split('@')]
            email_split = result_from_parsing[0]
            email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"
        elif DSM_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(randint(1, 99999)) + '@' + DSM_CATCHALL
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
            discord_webhook.raffle_to_webhook(email, site="DSM Entry", raffle=DSM_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')

            log_data.log_entry_data(site="DSM",
                                    raffle=DSM_RAFFLE_NAME,
                                    email=email,
                                    proxy=proxy_handler.parse_into_default_form(proxy),
                                    country='US',
                                    delay='Captcha'
                                    )

            session.close()

        else:
            if not DSM_CATCHALL_ENABLED and not DSM_PLUSTRICK_ENABLED:
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
            url=DSM_FORMSTACK_URL,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        
        return False
    try:
        phpsesh = resp.headers['Set-Cookie'].split(';')[0]

    except KeyError:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return False
    
    scraper.headers.update(
        {
            'referer': 'https://newyork.doverstreetmarket.com/new-items/raffle',
            'cookie': phpsesh
        }
    )

    try:
        resp = scraper.get(
            url=DSM_RAFFLE_URL,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('send_entry_requests')
        print(resp.content)
        print(scraper.cookies)

    captcha_token = captcha_handler.handle_captcha(DSM_RAFFLE_URL, DSM_DATA_SITEKEY)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False

    size = random.choice(shared_memory['sizes'])

    address = generate_address()
    
    def get_random_string(length):
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        result_str = ''.join(random.choice(letters) for _ in range(length))
        return result_str

    files = {
        'form': DSM_FORM_ID,
        'viewkey': DSM_VIEWKEY,
        'password': '',
        'hidden_fields': DSM_HIDDEN_FIELDS,
        'incomplete': '',
        'incomplete_password': '',
        'referrer': 'https://newyork.doverstreetmarket.com/',
        'referrer_type': 'js',
        '_submit': '1',
        'style_version': '3',
        'viewparam': DSM_VIEWPARAM,
        DSM_NAME_ID : name['first_name'] + ' ' + name['last_name'],
        DSM_EMAIL_ID : email,
        DSM_PHONE_ID : address['phone'],
        DSM_SIZE_ID : size,
        DSM_ADDRESS1_ID : address['address_1'],
        DSM_STATE_ID : address['state'],
        DSM_ZIP_ID : address['zip'],
        DSM_MAILING_ID: 'Please add me to the DSMNY mailing list',
        'g-recaptcha-response' : captcha_token,
        'nonce' : get_random_string(16),
    }

    if DSM_COLOR_ID != 'null':
        files[DSM_COLOR_ID] = DSM_COLOR
    else:
        if CONFIG.DEBUG_MODE:
            print('NO COLOR!')

    if DSM_QUESTION_ID != 'null':
        files[DSM_QUESTION_ID] = random.choice([
            "Travis Scott Dunk",
            "Kentucky",
            "Syracuse",
            "Brazil",
            "Michigan High",
            "Viotech",
            "PS",
            "Supreme Black",
            "Orange Skeleton",
            "Kentucky Dunk",
            "Off White Red",
            "Off White Orange",
            "Off White Green",
            "Infared",
            "",
        ])
    else:
        if CONFIG.DEBUG_MODE:
            print('NO COLOR!')

    m = MultipartEncoder(files, boundary=generate_boundary())

    scraper.headers.update(
        {
            'Content-type': m.content_type,
            'Origin': 'https://newyork.doverstreetmarket.com',
            'Referer': 'https://newyork.doverstreetmarket.com/',
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
        print('Raffle Entry Debug - ' + str(response.text))
        print('  Status - ' + str(response.status_code))
        print('  Cookies - ' + str(scraper.cookies))

    if str(scraper.get_redirect_target(
            response)) == DSM_SUCCESS_URL:
        success = True
    elif "The form was submitted successfully." in str(response.content):
        success = True
    elif 'Each submission must have unique values for the following fields. Please return and enter values that have not already been submitted' in str(response.content):
        success = True
    else:
        success = False

    return success


def generate_address():
    with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
        area_codes = list(file.read().splitlines())

    area_code = random.choice(area_codes)

    phone_number = area_code + str(randint(111, 999)) + str(randint(1000, 9999))

    if not CONFIG.USE_FAKER:
        real_address = address_api.get_address('US')
        address = {
            'address_1': real_address['address_1'],
            'city': real_address['city'],
            'zip': real_address['postcode'],
            'state': real_address['state'],
            'phone': phone_number,
        }

        if real_address['address_2'] != "" or real_address['address_2'] != real_address['address_1']:
            address['address_1'] = address['address_1'] + ' ' + real_address['address_2']
        address['state'] = info_generator.convert_state(address['state'])

    else:
        fake = Faker('en_US')

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.zipcode(),
            'state': fake.state(),
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
    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/DSM_' + DSM_RAFFLE_NAME + '.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/DSM_' + DSM_RAFFLE_NAME + '.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="DSM", raffle=DSM_RAFFLE_NAME)
