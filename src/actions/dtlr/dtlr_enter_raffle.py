from src.handlers import captcha_handler, proxy_handler, email_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils, address_api, info_generator
import config as CONFIG
import random
import time
import logging
import json
import string
import os
import threading
from faker import Faker
from random import randint
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected
from requests_toolbelt import MultipartEncoder

'''
DTLR ENTRY CONFIG
'''

DTLR_RAFFLE_URL = ''
DTLR_RAFFLE_NAME = ''
DTLR_RAFFLE_NUMBER = ''
DTLR_GS_SIZING = False
DTLR_DATA_SITEKEY = '6LeepqwUAAAAAKmQ_Dj-bY23bKZtThXNxlxFKp6F'

DTLR_PLUSTRICK_ENABLED = False
DTLR_GMAIL = ''

def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_list = []
    with open(CONFIG.ROOT + '/data/emails/emails.json', 'r') as json_file:
        data = json.load(json_file)
        for email in data['emails']:
            email_list.append(email.split(':')[0])

    proxies = proxy_handler.get_proxy_list()
    email_queue = email_handler.get_email_queue()

    if DTLR_GS_SIZING:
        sizes = ['4', '4.5', '5', '5.5', '6', '6.5', '7']
    else:
        sizes = ['7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '13']

    return {
        'email_queue': email_queue,
        'email_list': email_list,
        'proxies': proxies,
        'sizes': sizes
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        fake = Faker()
        name = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name()
        }

        if DTLR_PLUSTRICK_ENABLED:
            if CONFIG.DEBUG_MODE:
                result_from_parsing = [x.strip() for x in random.choice(shared_memory['email_list']).split('@')]
                email_split = result_from_parsing[0]
                email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"
            else:
                result_from_parsing = [x.strip() for x in DTLR_GMAIL.split('@')]
                email_split = result_from_parsing[0]
                email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"

        else:
            unparsed_email = shared_memory['email_queue'].get()
            email = unparsed_email.get_email()
            if unparsed_email.nameEnabled():
                name = {
                    'first_name': unparsed_email.get_first_name(),
                    'last_name': unparsed_email.get_last_name()
                }

        if CONFIG.DEBUG_MODE:
            DTLR_WEBHOOK = False
        else:
            DTLR_WEBHOOK = True

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

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')
            if DTLR_WEBHOOK:
                discord_webhook.raffle_to_webhook(email, site="DTLR Entry", raffle=DTLR_RAFFLE_NAME)

                log_data.log_entry_data(site="DTLR",
                                        raffle=DTLR_RAFFLE_NAME,
                                        email=email,
                                        proxy=proxy_handler.parse_into_default_form(proxy),
                                        delay='Captcha'
                                        )

            session.close()

        else:
            if not DTLR_PLUSTRICK_ENABLED:
                shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            session.close()
            time.sleep(1)


def send_entry_requests(email, name, scraper, proxy, shared_memory):
    scraper.headers.update(
        {
            'referer': 'https://www.dtlr.com/'
        }
    )

    try:
        resp = scraper.get(
            url=DTLR_RAFFLE_URL,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print(resp.content)
        print(scraper.cookies)

    captcha_token = captcha_handler.handle_captcha(DTLR_RAFFLE_URL, DTLR_DATA_SITEKEY)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False

    size = random.choice(shared_memory['sizes'])

    address = generate_address()

    state = address['state']
    if len(state) == 2:
        state = info_generator.convert_state(state)

    files = {
        'input_3.3': name['first_name'],
        'input_3.6': name['last_name'],
        'input_4': email,
        'input_4_2': email,
        'input_15': str(randint(1990, 2001)),
        'input_7': address['phone'],
        'input_10.1': address['address_1'].rstrip(),
        'input_10.3': address['city'],
        'input_10.4': state,
        'input_10.5': address['zip'],
        'input_10.6': 'United States',
        'input_12': 'Male',
        'input_13': size,
        'input_19': 'on',
        'g-recaptcha-response': captcha_token,
        'input_20': '',
        'is_submit_' + DTLR_RAFFLE_NUMBER: '1',
        'gform_submit': DTLR_RAFFLE_NUMBER,
        'gform_unique_id': '',
        'state_' + DTLR_RAFFLE_NUMBER: 'WyJbXSIsImY0MTdjODMxMmY0YzlhNTIzMTkzNWQ5ZWQ5MDdkNTQzIl0=',
        'gform_target_page_number_' + DTLR_RAFFLE_NUMBER: '0',
        'gform_source_page_number_' + DTLR_RAFFLE_NUMBER: '1',
        'gform_field_values': ''
    }

    m = MultipartEncoder(files, boundary=generate_boundary())

    scraper.headers.update({
        'Content-Type': m.content_type,
        'Referer': DTLR_RAFFLE_URL,
        'Origin': 'https://blog.dtlr.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
    })

    try:
        response = scraper.post(
            url=DTLR_RAFFLE_URL,
            data=m.to_string(),
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

    if 'Almost There' in response.text:
        success = True
    else:
        success = False

    return success


def email_already_entered(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def generate_address():
    fake = Faker('en_US')

    with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
        area_codes = list(file.read().splitlines())

    area_code = random.choice(area_codes)

    phone_number = '(' + area_code + ') ' + str(randint(111, 999)) + "-" + str(randint(1000,9999))

    fake_state_abbr = fake.state_abbr()
    if CONFIG.USE_FAKER:
        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'state': info_generator.convert_state(fake_state_abbr),
            'zip': fake.postalcode_in_state(fake_state_abbr),
            'phone': phone_number,
            'country': 'United States'
        }

        return address

    else:
        real_address = address_api.get_address('US')

        address = {
            'address_1': real_address['address_1'].rstrip(),
            'city': real_address['city'],
            'zip': real_address['postcode'],
            'state': info_generator.convert_state(real_address['state']),
            'phone': phone_number,
            'country': 'United States'
        }

        if real_address['address_2'] != "" or real_address['address_2'] != real_address['address_1']:
            address['address_1'] = (address['address_1'] + ' ' + real_address['address_2']).rstrip()

        return address


def generate_boundary(size=16):
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits +
                                 string.ascii_lowercase, k=size))

    prefix = '------WebKitFormBoundary'

    return prefix + res


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="DTLR Entry", raffle=DTLR_RAFFLE_NAME)
