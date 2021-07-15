from src.handlers import proxy_handler
from src.utils import discord_webhook, cloudscraper_utils
import config as CONFIG
import queue
import random
import time
import os
import json
import logging

from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected


'''
DTLR Raffle Confirmation
'''
DTLR_RAFFLE_NAME = ''
DTLR_DEFAULT_URL = 'http://email.ecommail.dtlr.com/c/'

def init():
    print("Beginning Raffle Confirmations...\n")

    logging.info("Beginning Raffle Confirmations...")

    TOKEN_FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_tokens.txt'


    proxies = None
    with open(CONFIG.ROOT + '/data/proxies/proxy_lists.json', 'r') as json_file:
        data = json.load(json_file)

        list_id = 0
        while list_id < len(data['proxies']):
            if data['proxies'][list_id]['list_name'] == CONFIG.PROXY_LIST_NAME:
                break

        unformatted_proxy_list = data['proxies'][list_id]['proxies']
        proxies = proxy_handler.parse_into_request_format(unformatted_proxy_list)

    email_queue = None

    try:
        with open(TOKEN_FILE_PATH, 'r') as file:
            emails = list(file.read().split())
            email_queue = queue.Queue()
            [email_queue.put(a) for a in emails]
    except IOError:
        if not os.path.exists(TOKEN_FILE_PATH):
            file = open(TOKEN_FILE_PATH, 'w+')
            file.close()

            logging.info('[Error] - Token file does not exist! Please run the DTLR Token Collector First.')
            print('[Error] - Token file does not exist! Please run the DTLR Token Collector First.')

    return {
        'email_queue': email_queue,
        'proxies': proxies
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        email = shared_memory['email_queue'].get()

        if 'email.ecommail.dtlr.com' in email:
            result_from_parsing = [x.strip() for x in email.split('/')]
            entry = {
                'email': "Unknown",
                'token': result_from_parsing[-1],
            }
        else:
            result_from_parsing = [x.strip() for x in email.split(':')]
            entry = {
                'email': result_from_parsing[0],
                'token': result_from_parsing[1],
            }

        if token_already_confirmed(entry['token']):
            continue

        if CONFIG.DEBUG_MODE:
            DTLR_WEBHOOK = False
        else:
            DTLR_WEBHOOK = True

        scraper = cloudscraper_utils.create_scraper()

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

        successfully_entered = send_raffle_entry_request(scraper, entry, proxy)

        if successfully_entered:
            write_email_to_file(entry['token'])

            if DTLR_WEBHOOK:
                discord_webhook.confirmation_to_webhook(entry['email'], site="DTLR", raffle=DTLR_RAFFLE_NAME)

            print(f'Successfully confirmed {entry["email"]} at {time.strftime("%I:%M:%S")}')
            logging.info(f'Successfully confirmed {entry["email"]} at {time.strftime("%I:%M:%S")}')
            scraper.close()
            time.sleep(1)

        else:
            shared_memory['email_queue'].put(email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("Failed to enter raffle with account. Adding account back to queue.")

            scraper.close()
            time.sleep(1)


def send_raffle_entry_request(scraper, entry, proxy):
    url = DTLR_DEFAULT_URL + entry['token']

    try:
        response = scraper.get(
            url=url,
            proxies=proxy,
            timeout=30
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print(response.content)
        print(response.status_code)
        print(scraper.cookies)

    if 'Thank You For Entering' in response.text or 'cURL error 60' in response.text:
        return True
    else:
        return False


def token_already_confirmed(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_confirmations.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_email_to_file(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_confirmations.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + '\n')


# def get_proxy_of_entry(email):
#     try:
#         ENTRY_FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_entries.txt'
#     except IOError:
#         logging.info('[Error] - Entry file does not exist! Please run DTLR Raffle Entry First.')
#
#     with open(ENTRY_FILE_PATH, 'r') as file:
#         for line in file:
#             if email in line:
#                 result_from_parsing = [x.strip() for x in line.split(':')]
#                 if len(result_from_parsing) == 5:
#                     proxy = (result_from_parsing[1] + ':' +
#                              result_from_parsing[2] + ':' +
#                              result_from_parsing[3] + ':' +
#                              result_from_parsing[4]
#                              )
#                 else:
#                     proxy = (result_from_parsing[1] + ':' +
#                              result_from_parsing[2]
#                              )
#                 return proxy
#
#     return 'Proxy Not Found!'


def shutdown():
    discord_webhook.raffle_entry_complete(site="DTLR Confirmations", raffle=DTLR_RAFFLE_NAME, confirmation=True)
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")

