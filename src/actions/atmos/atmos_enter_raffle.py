from src.handlers import proxy_handler, captcha_handler, email_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils, address_api
import config as CONFIG
import random
import time
import logging
import os
from pathlib import Path
import threading
from faker import Faker
from random import randint
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected

'''
ATMOS ENTRY CONFIG
'''
ATMOS_RAFFLE_NAME = ''
ATMOS_RELEASE_ID = ''
ATMOS_STORE_ID = ''

ATMOS_PLUSTRICK_ENABLED = False
ATMOS_GMAIL = ''

ATMOS_CATCHALL_ENABLED = False
ATMOS_CATCHALL = ''

ATMOS_DATA_SITEKEY = '6LcES6sZAAAAACGrj8rrJm13isYkVke0iBaZwtaF'


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_queue = email_handler.get_email_queue()

    area_codes = None
    with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
        area_codes = list(file.read().splitlines())

    instagram_followers = None
    with open(CONFIG.ROOT + '/data/social_media/atmos_instagram.txt', 'r') as file:
        instagram_followers = list(file.read().splitlines())

    proxies = proxy_handler.get_proxy_list()

    sizes = ["8", "8_5", "9", "9_5", "10", "10_5", "11", "11_5", "12", "13"]

    return {
        'email_queue': email_queue,
        'proxies': proxies,
        'instagrams': instagram_followers,
        'area_codes': area_codes,
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

        if ATMOS_PLUSTRICK_ENABLED:
            result_from_parsing = [x.strip() for x in ATMOS_GMAIL.split('@')]
            email_split = result_from_parsing[0]
            email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"
        elif ATMOS_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(randint(10, 99)) + '@' + ATMOS_CATCHALL
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
            discord_webhook.raffle_to_webhook(email, site="ATMOS Entry", raffle=ATMOS_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info(
                "[" + threading.currentThread().getName() + "] " + f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')

            log_data.log_entry_data(site="ATMOS",
                                    raffle=ATMOS_RAFFLE_NAME,
                                    email=email,
                                    proxy=proxy_handler.parse_into_default_form(proxy),
                                    country='US',
                                    delay='Captcha'
                                    )

            session.close()

        else:
            if not ATMOS_CATCHALL_ENABLED and not ATMOS_PLUSTRICK_ENABLED:
                shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle. Adding email back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle. Adding email back to queue.")
            session.close()
            time.sleep(1)


def send_entry_requests(email, name, scraper, proxy, shared_memory):
    captcha_token = captcha_handler.handle_captcha('https://releases.atmosusa.com/entry', ATMOS_DATA_SITEKEY)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False

    size = random.choice(shared_memory['sizes'])
    instagram = random.choice(shared_memory['instagrams'])

    address = generate_address(random.choice(shared_memory['area_codes']))

    data = {
        'release': ATMOS_RELEASE_ID,
        'size': size,
        'email': email,
        'confirmEmail': email,
        'firstName': name['first_name'],
        'lastName': name['last_name'],
        'zipCode': address['zip'],
        'instagramHandle': instagram,
        'phoneNumber': address['phone'],
        'recaptcha': captcha_token,
        'address1': address['address_1'],
        'address2': None,
        'state': address['state'],
        'city': address['city'],
        'store': ATMOS_STORE_ID
    }

    scraper.headers.update(
        {
            'Content-Type': 'application/json',
            'Origin': 'https://releases.atmosusa.com',
            'Referer': 'https://releases.atmosusa.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'dnt': '1'
        }
    )

    try:
        response = scraper.post(
            url='https://stage-ubiq-raffle-strapi-be.herokuapp.com/entries',
            json=data,
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

    if response.ok:
        success = True
    else:
        success = False

    return success


def generate_address(area_code):
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

        # if real_address['address_2'] != "" or real_address['address_2'] != real_address['address_1']:
        #     address['address_1'] = address['address_1'] + ' ' + real_address['address_2']

    else:
        fake = Faker('en_US')

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.zipcode(),
            'state': fake.state(),
            'phone': phone_number,
        }
    print(address['state'])
    return address


def email_already_entered(email):
    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/ATMOS_' + ATMOS_RAFFLE_NAME + '.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/ATMOS_' + ATMOS_RAFFLE_NAME + '.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="ATMOS", raffle=ATMOS_RAFFLE_NAME)
