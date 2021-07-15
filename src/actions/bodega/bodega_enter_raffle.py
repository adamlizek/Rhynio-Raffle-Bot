from src.handlers import proxy_handler, captcha_handler, email_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils
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
BODEGA ENTRY CONFIG
'''
BODEGA_RAFFLE_WEBPAGE = ''
BODEGA_RAFFLE_URL = ''
BODEGA_DATA_SITE_KEY = '6LdhYxYUAAAAAAcorjMQeKmZb6W48bqb0ZEDRPCl'
BODEGA_RAFFLE_NAME = ''
BODEGA_PID = ''
BODEGA_RNDID = ''
BODEGA_POST_ID = ''
BODEGA_SIZE_ID = ''
BODEGA_REFERER_HEADER = ''
BODEGA_INSTAGRAM_ID = ''
BODEGA_STYLE = ''
BODEGA_STYLE_ID = ''

BODEGA_PLUSTRICK_ENABLED = False
BODEGA_GMAIL = ''

BODEGA_CATCHALL_ENABLED = False
BODEGA_CATCHALL = ''


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    email_queue = email_handler.get_email_queue()
    proxies = proxy_handler.get_proxy_list()

    sizes = ['5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5',
             '10', '10.5', '11', '11.5', '12', '13']

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

        if BODEGA_PLUSTRICK_ENABLED:
            result_from_parsing = [x.strip() for x in BODEGA_GMAIL.split('@')]
            email_split = result_from_parsing[0]
            email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"
        elif BODEGA_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(randint(10, 99)) + '@' + BODEGA_CATCHALL
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
            discord_webhook.raffle_to_webhook(email, site="BODEGA Entry", raffle=BODEGA_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully registered {email} at {time.strftime("%I:%M:%S")}')

            log_data.log_entry_data(site="BODEGA",
                                    raffle=BODEGA_RAFFLE_NAME,
                                    email=email,
                                    proxy=proxy_handler.parse_into_default_form(proxy),
                                    country='US',
                                    delay='Captcha'
                                    )

            session.close()

        else:
            if not BODEGA_CATCHALL_ENABLED and not BODEGA_PLUSTRICK_ENABLED:
                shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            session.close()
            time.sleep(1)


def send_entry_requests(email, session, proxy, name, shared_memory):
    # ==============================
    # Request 1 - GET raffle webpage
    # ==============================
    try:
        resp = session.get(
            url=BODEGA_RAFFLE_WEBPAGE,
            proxies=proxy
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False



    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    # =================================
    # Request 3 - POST viralsweep token
    # =================================
    # try:
    #     soup = BeautifulSoup(resp.text, 'html.parser')
    #     TI = soup.find('input', {'name': 'ti'}).get('value')
    #     print(TI)
    #     if CONFIG.DEBUG_MODE:
    #         print(TI)
    #
    # except Exception:
    #     print("Error: " + proxy['https'] + " is bad!")
    #     logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
    #     return False
    #
    # if CONFIG.DEBUG_MODE:
    #     print(resp.content)
    #     print(session.cookies)
    #
    # session.headers.update(
    #     {
    #         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #         'Origin': 'https://app.viralsweep.com',
    #         'Referer': BODEGA_REFERER_HEADER,
    #         'X-Requested-With': 'XMLHttpRequest'
    #     }
    # )
    #
    # data = {
    #     'id': TI,
    #     'pid': BODEGA_PID
    # }
    #
    # try:
    #     resp = session.post(
    #         url='https://app.viralsweep.com/promo/token',
    #         data=data,
    #         proxies=proxy
    #     )
    #
    # except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
    #     print("Proxy Error Handled - " + str(e))
    #     return False


    # =================================
    # Request 4 - POST viralsweep enter
    # =================================
    # changes
    #   email again is empty?
    #   entry source is just bdgastore
    #   refer source changed
    #   cookie - vs entry id
    # TV = resp.text
    #
    # print(TV)
    #
    # if len(TV) < 10:
    #     return False
    #
    # if CONFIG.DEBUG_MODE:
    #     print(TV)

    captcha_token = captcha_handler.handle_captcha(captcha_url=BODEGA_RAFFLE_URL, captcha_data_site_key=BODEGA_DATA_SITE_KEY)

    print(captcha_token)

    if len(captcha_token) < 10:
        return False

    size = random.choice(shared_memory['sizes'])

    data = {
        'id': BODEGA_POST_ID,
        'type': 'widget',
        'rfid': '',
        'cpid': '',
        'refer_source': 'https://bdgastore.com/blogs/upcoming-releases',
        'entry_source': BODEGA_RAFFLE_WEBPAGE,
        'first_name': name['first_name'],
        'last_name': name['last_name'],
        'email': email,
        'email_again': '',
        BODEGA_SIZE_ID: size,
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

    print("Made 4th Req")

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.content))
        print('  Status - ' + str(response.status_code))
        print('  Cookies - ' + str(session.cookies))

    print(response.content)

    if '{"success":1' in str(response.content):
        success = True
    else:
        success = False


    # 2 BONUS ENTRIES - CURRENTLY DISABLED
    def bonus_entries():
        try:
            resp = session.get(
                url=BODEGA_RAFFLE_URL,
                proxies=proxy
            )
        except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
            print("Proxy Error Handled - " + str(e))
            return

        try:
            soup = BeautifulSoup(resp.text, 'html.parser')
            EID_HASH = soup.find('input', {'id': 'entry_hash'}).get('value')
            AID = soup.find('li', {'data-tep': BODEGA_INSTAGRAM_ID}).get('data-aid')
            print(EID_HASH)
            print(AID)

            if CONFIG.DEBUG_MODE:
                print(EID_HASH)
                print(AID)
        except Exception:
            print("Error: " + proxy['https'] + " is bad!")
            logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
            return

        data = {
            'aid': AID,
            'type': 'instagram',
            'pid': BODEGA_PID,
            'extra': '',
            'eid_hash': EID_HASH

        }

        try:
            resp = session.post(
                url='https://app.viralsweep.com/promo/bonus',
                data=data,
                proxies=proxy
            )
        except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
            print("Proxy Error Handled - " + str(e))

        if CONFIG.DEBUG_MODE:
            print(resp.content)
    #bonus_entries()

    return success


def email_already_entered(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/BODEGA_' + BODEGA_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email, proxy):
    proxy = proxy_handler.parse_into_default_form(proxy)

    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/BODEGA_' + BODEGA_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ':' + proxy + '\n')


def shutdown():
    print("\nThere are no more emails remaining to enter! Shutting down.")
    logging.info("There are no more emails remaining to enter! Shutting down.")
    discord_webhook.raffle_entry_complete(site="BODEGA Entry", raffle=BODEGA_RAFFLE_NAME)
