from src.handlers import proxy_handler, captcha_handler, email_handler
from src.utils import discord_webhook, log_data, faker_generator, cloudscraper_utils, address_api, info_generator
import config as CONFIG
import random
import time
import logging
import os
import threading
from bs4 import BeautifulSoup
from faker import Faker
from random import randint
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected

'''
UNDEFEATED ENTRY CONFIG
'''

UNDEFEATED_RAFFLE_WEBPAGE = ''
UNDEFEATED_RAFFLE_URL = ''
UNDEFEATED_DATA_SITE_KEY = '6LdhYxYUAAAAAAcorjMQeKmZb6W48bqb0ZEDRPCl'
UNDEFEATED_RAFFLE_NAME = ''
UNDEFEATED_PID = ''
UNDEFEATED_RNDID = ''
UNDEFEATED_POST_ID = ''
UNDEFEATED_QUESTION_ANSWER = ''
UNDEFEATED_STYLE = ''

UNDEFEATED_PLUSTRICK_ENABLED = False
UNDEFEATED_GMAIL = ''

UNDEFEATED_CATCHALL_ENABLED = True
UNDEFEATED_CATCHALL = ''


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_queue = email_handler.get_email_queue()
    proxies = proxy_handler.get_proxy_list()

    sizes = ['4', '5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9',
             '10', '10.5', '11', '11.5', '12', '13', '14']

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

        if UNDEFEATED_PLUSTRICK_ENABLED:
            result_from_parsing = [x.strip() for x in UNDEFEATED_GMAIL.split('@')]
            email_split = result_from_parsing[0]
            email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"
        elif UNDEFEATED_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(randint(10, 99)) + '@' + UNDEFEATED_CATCHALL
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
        successfully_entered = send_entry_requests(email, session, proxy, name, shared_memory)

        if successfully_entered:
            write_account_to_file(email, proxy)
            discord_webhook.raffle_to_webhook(email, site="UNDEFEATED Entry", raffle=UNDEFEATED_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')

            log_data.log_entry_data(site="UNDEFEATED",
                                    raffle=UNDEFEATED_RAFFLE_NAME,
                                    email=email,
                                    proxy=proxy_handler.parse_into_default_form(proxy),
                                    country='US',
                                    delay='Captcha'
                                    )

            session.close()

        else:
            if not UNDEFEATED_CATCHALL_ENABLED and not UNDEFEATED_PLUSTRICK_ENABLED:
                shared_memory['email_queue'].put(unparsed_email)
            shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            session.close()
            time.sleep(1)


def send_entry_requests(email, session, proxy, name):
    try:
        resp = session.get(
            url=UNDEFEATED_RAFFLE_WEBPAGE,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    session.headers.update(
        {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': UNDEFEATED_RAFFLE_URL,
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
        }
    )

    data = (
        ('rndid ', UNDEFEATED_RNDID),
        ('framed', '1'),
        ('ref', ''),
        ('source_url', UNDEFEATED_RAFFLE_WEBPAGE),
        ('hash', ''),
        ('vs_eid_hash', '')
    )

    try:
        resp = session.get(
            url=UNDEFEATED_RAFFLE_URL,
            params=data,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    # Getting TI
    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
        TI = soup.find('input', {'name': 'ti'}).get('value')
        if CONFIG.DEBUG_MODE:
            print(TI)
    except Exception:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return False

    if CONFIG.DEBUG_MODE:
        print(resp.content)
        print(session.cookies)

    session.headers.update(
        {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://app.viralsweep.com',
            'referer': UNDEFEATED_RAFFLE_URL,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest'
        }
    )

    data = {
        'id': TI,
        'pid': UNDEFEATED_PID
    }

    try:
        resp = session.post(
            url='https://app.viralsweep.com/promo/token',
            data=data,
            proxies=proxy
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    TV = resp.text
    if len(TV) < 10:
        return False

    if CONFIG.DEBUG_MODE:
        print(TV)

    address = generate_address()

    captcha_token = captcha_handler.handle_captcha(captcha_url=UNDEFEATED_RAFFLE_URL, captcha_data_site_key=UNDEFEATED_DATA_SITE_KEY)

    if len(captcha_token) < 10:
        print(captcha_token)
        return False

    if len(address['state']) == 2:
        state = info_generator.convert_state(address['state'])
    else:
        state = address['state']
    print(state)
    data = {
        'id': UNDEFEATED_POST_ID,
        'type': 'widget',
        'tv': TV,
        'ti': TI,
        'cpid': '',
        'rfid': '',
        'refer_source': '',
        'entry_source': UNDEFEATED_RAFFLE_WEBPAGE,
        'first_name': name['first_name'],
        'last_name': name['last_name'],
        'email': email,
        'email_again': email,
        'address': address['address_1'].rstrip(),
        'city': address['city'],
        'state': address['state'],
        'zip': address['zip'],
        '20335_1557256722': random.choice(['7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11']),
        '52904_1591653435': UNDEFEATED_QUESTION_ANSWER,
        '65239_1557525654': UNDEFEATED_STYLE,
        '86218_1557267602': 'yes',
        'newsletter_subscribe': 'yes',
        'agree_to_rules': 'yes',
        'g-recaptcha-response': captcha_token
    }
    # print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in data.items()) + "}")

    try:
        response = session.post(
            url='https://app.viralsweep.com/promo/enter',
            data=data,
            proxies=proxy,
            timeout=45
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.content))
        print('  Status - ' + str(response.status_code))
        print('  Cookies - ' + str(session.cookies))

    if '{"success":1' in str(response.content):
        success = True
    else:
        success = False

    return success


def email_already_entered(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/UNDEFEATED_' + UNDEFEATED_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/UNDEFEATED_' + UNDEFEATED_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def generate_address():
    country = 'United States'

    if not CONFIG.USE_FAKER:
        try:
            real_address = address_api.get_address(country)

            address = {
                'address_1': real_address['address_1'],
                'city': real_address['city'],
                'zip': real_address['postcode'],
                'state': real_address['state'],
                'country': 'US'
            }


            real_address['state'] = info_generator.convert_state(real_address['state'])

            if real_address['address_2'] != "" or real_address['address_2'] != real_address['address_1']:
                address['address_1'] = address['address_1'] + ' ' + real_address['address_2']
        except TypeError:
            address = faker_generator.generate_naked_address(country)

    else:
        address = faker_generator.generate_naked_address(country)
    if CONFIG.DEBUG_MODE:
        print(address)

    return address


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="UNDEFEATED Entry", raffle=UNDEFEATED_RAFFLE_NAME)

