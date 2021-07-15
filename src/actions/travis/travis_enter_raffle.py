from src.handlers import proxy_handler
from src.utils import discord_webhook, cloudscraper_utils, faker_generator
import config as CONFIG
import queue
import time
import logging
import json
import os
import random
import threading
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected

import pprint

'''	
TRAVIS Raffle Entry	
'''

TRAVIS_RAFFLE_NAME = ''

TRAVIS_CATCHALL_ENABLED = False
TRAVIS_CATCHALL = ''


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


    us_cities = None
    with open(CONFIG.ROOT + '/data/info/cities.txt', 'r') as file:
        us_cities = list(file.read().splitlines())

    sizes = ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5',
             '11', '11.5', '12', '12.5', '13', '14']

    global OUTPUT_FILE_PATH
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Travis_' + TRAVIS_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    return {
        'sizes': sizes,
        'us_cities': us_cities,
        'proxies': proxies,
        'email_queue': email_queue
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email

    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        fake = faker_generator.generate_country_faker('United States')
        name = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name()
        }

        if TRAVIS_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(random.randint(10, 99)) + '@' + TRAVIS_CATCHALL
        else:
            email = shared_memory['email_queue'].get()

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
        address = generate_address(shared_memory)

        successfully_entered = send_entry_requests(email, scraper, name, proxy, address)

        if successfully_entered:
            write_account_to_file(email, proxy)
            discord_webhook.raffle_to_webhook(email, site="Travis Entry", raffle=TRAVIS_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')

            scraper.close()

        else:
            shared_memory['email_queue'].put(email)
            print("Failed to enter raffle with account. Adding account back to queue.")

            scraper.close()
            time.sleep(1)


def send_entry_requests(email, scraper, name, proxy, address):
    url = 'https://shop.travisscott.com/products/travis-scott-nike-air-max-270-cactus-trails-signup'

    try:
        initial = scraper.get(
            url=url,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Initial - ' + str(initial.status_code))
        print('Cookies - ' + str(scraper.cookies))

    data = (
        ('a', 'm'),
        ('email', email),
        ('first', name['first_name']),
        ('last', name['last_name']),
        ('zip', address['zip_code']),
        ('telephone', address['phone']),
        ('product_id', '4376272470143'),
        ('size', address['size'])
    )

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)
    time.sleep(random.randint(1, 15))

    scraper.headers.update(
        {
            'origin': 'https://shop.travisscott.com',
            'referer': url,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site'
        }
    )

    try:
        response = scraper.get(
            url='https://dom33edp2m.execute-api.us-east-1.amazonaws.com/stage/submit',
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

    if 'thanks' in response.text:
        success = True
    else:
        success = False

    return success


def email_already_entered(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Travis_' + TRAVIS_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Travis_' + TRAVIS_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    proxy = proxy_handler.parse_into_default_form(proxy)

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def generate_address(shared_memory):
    country = 'United States'
    zip_city_state = random.choice(shared_memory['us_cities'])

    result_from_parsing = [x.strip() for x in zip_city_state.split(':')]
    zip = result_from_parsing[0]
    city = result_from_parsing[1]
    state = result_from_parsing[2]

    address_info = {
        "zip_code": zip,
        "city": city,
        "state": state,
        "phone": str(random.randint(1000000000, 9999999999)),
        "country": country,
        "size": random.choice(shared_memory['sizes'])
    }

    return address_info


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="Travis Entry", raffle=TRAVIS_RAFFLE_NAME)