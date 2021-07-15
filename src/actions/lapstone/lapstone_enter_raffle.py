from src.handlers import proxy_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils, address_api
import config as CONFIG
import queue
import random
import time
import logging
import os
import json
import threading
from random import randint
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected
from enum import Enum
from faker import Faker
from pathlib import Path

'''
LAPSTONE ENTRY CONFIG
'''

LAPSTONE_RAFFLE_URL = ''
LAPSTONE_RAFFLE_NAME = ''

LAPSTONE_RAFFLE_U = ''
LAPSTONE_RAFFLE_ID = ''
LAPSTONE_RAFFLE_FAKE_PARAM = ''
LAPSTONE_DELAY = 15
LAPSTONE_ANSWER = ''

class socialMode(Enum):
    TWITTER = 1
    INSTAGRAM = 2


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_queue = None
    with open(CONFIG.ROOT + '/data/emails/emails.json', 'r') as json_file:
        data = json.load(json_file)
        email_queue = queue.Queue()
        [email_queue.put(e) for e in data['emails']]

    proxies = None
    with open(CONFIG.ROOT + '/data/proxies/proxy_lists.json', 'r') as json_file:
        data = json.load(json_file)

        list_id = 0
        while list_id < len(data['proxies']):
            if data['proxies'][list_id]['list_name'] == CONFIG.PROXY_LIST_NAME:
                break

        unformatted_proxy_list = data['proxies'][list_id]['proxies']
        proxies = proxy_handler.parse_into_request_format(unformatted_proxy_list)

    instagram_followers = None
    with open(CONFIG.ROOT + '/data/social_media/lapstone_instagram.txt', 'r') as file:
        instagram_followers = list(file.read().splitlines())

    twitter_followers = None
    with open(CONFIG.ROOT + '/data/social_media/lapstone_twitter.txt', 'r') as file:
        twitter_followers = list(file.read().splitlines())

    sizes = ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5',
             '11', '12']

    return {
        'email_queue': email_queue,
        'proxies': proxies,
        'instagrams': instagram_followers,
        'twitters': twitter_followers,
        'sizes': sizes
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        unparsed_email = shared_memory['email_queue'].get()
        email = unparsed_email.get_email()

        if email_already_entered(email):
            continue

        fake = Faker()

        if unparsed_email.nameEnabled():
            first_name = unparsed_email.get_first_name()
            last_name = unparsed_email.get_last_name()
        else:
            first_name = fake.first_name()
            last_name = fake.last_name()

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

        scraper = cloudscraper_utils.create_scraper()

        # make registration request & verify
        successfully_entered = send_entry_requests(email, first_name, last_name,
                                                   scraper, proxy, shared_memory)

        if successfully_entered:
            write_account_to_file(email, proxy)
            discord_webhook.raffle_to_webhook(email, site="Lapstone Entry", raffle=LAPSTONE_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')

            log_data.log_entry_data(site="LAPSTONE",
                                    raffle=LAPSTONE_RAFFLE_NAME,
                                    email=email,
                                    proxy=proxy_handler.parse_into_default_form(proxy),
                                    delay=LAPSTONE_DELAY
                                    )

            scraper.close()
            time.sleep(int(LAPSTONE_DELAY))

        else:
            shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            scraper.close()
            time.sleep(1)


def send_entry_requests(email, first_name, last_name, scraper, proxy, shared_memory):
    url = LAPSTONE_RAFFLE_URL

    try:
        resp = scraper.get(
            url=url,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print(resp.content)
        print(scraper.cookies)

    u = LAPSTONE_RAFFLE_U
    id = LAPSTONE_RAFFLE_ID
    fake_param = LAPSTONE_RAFFLE_FAKE_PARAM

    size = random.choice(shared_memory['sizes'])

    instagram = random.choice(shared_memory['instagrams'])
    twitter = random.choice(shared_memory['twitters'])

    time.sleep(randint(10, 20))

    time_param = int(time.time())
    c = 'jQuery19000464' + str(randint(11111111111111, 99999999999999)) + '_' + str(time_param)

    data = (
        ('u', u),
        ('id', id),
        ('c', c),
        ('EMAIL', email),
        ('FNAME', first_name),
        ('LNAME', last_name),
        ('MMERGE3', 'Online Shipping'),
        ('MMERGE4', size),
        ('MMERGE5', twitter),
        ('MMERGE6', instagram),
        (fake_param, ''),
        ('subscribe', 'Submit'),
        ('_', str(time_param+1))
    )

    scraper.headers.update({
        'Referer': 'https://www.lapstoneandhammer.com/',
    })

    try:
        response = scraper.get(
            url='https://lapstoneandhammer.us10.list-manage.com/subscribe/post-json',
            params=data,
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

    if '"result":"success","msg":"Almost finished...' in response.text:
        success = True
    else:
        success = False

    return success

def generate_address():
    with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
        area_codes = list(file.read().splitlines())

    area_code = random.choice(area_codes)

    phone_number = area_code + str(randint(111, 999)) + "-" + str(randint(1000,9999))

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

def email_already_entered(email):
    OUTPUT_FILE_PATH = Path(CONFIG.ROOT + '/output/Lapstone_' + LAPSTONE_RAFFLE_NAME + '_entries.txt')

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Lapstone_' + LAPSTONE_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="Lapstone Entry", raffle=LAPSTONE_RAFFLE_NAME)
