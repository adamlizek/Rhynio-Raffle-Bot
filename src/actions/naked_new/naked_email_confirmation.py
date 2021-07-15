from src.handlers import proxy_handler
from src.utils import discord_webhook, cloudscraper_utils
import config as CONFIG
import queue
import random
import time
import os
import logging

from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected

'''
NAKED Raffle Confirmation
'''
NAKED_RAFFLE_NAME = ''


def init():
    print("Beginning Raffle Confirmations...\n")
    logging.info("Beginning Raffle Confirmations...")

    TOKEN_FILE_PATH = CONFIG.ROOT + '/output/nakednew/Naked_' + NAKED_RAFFLE_NAME + '_tokens.txt'

    try:
        email_queue = None
        with open(TOKEN_FILE_PATH, 'r') as file:
            emails = list(file.read().split())
            email_queue = queue.Queue()
            [email_queue.put(a) for a in emails]
    except IOError:
        if not os.path.exists(TOKEN_FILE_PATH):
            file = open(TOKEN_FILE_PATH, 'w+')
            file.close()
        logging.info('[Error] - Token file does not exist! Please run the Naked Token Collector First.')

    proxies = proxy_handler.get_proxy_list()

    return {
        'email_queue': email_queue,
        'proxies': proxies
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        email = shared_memory['email_queue'].get()

        result_from_parsing = [x.strip() for x in email.split(':')]
        entry = {
            'email': result_from_parsing[0],
            'token': result_from_parsing[1]
        }

        if email_already_confirmed(entry['email']):
            continue

        scraper = cloudscraper_utils.create_scraper()

        successfully_entered = send_raffle_entry_request(scraper, entry, shared_memory)

        if successfully_entered:
            write_email_to_file(entry['email'])
            discord_webhook.confirmation_to_webhook(entry['email'], site="Naked", raffle=NAKED_RAFFLE_NAME)

            print(f'Successfully confirmed {entry["email"]} at {time.strftime("%I:%M:%S")}')
            logging.info(f'Successfully confirmed {entry["email"]} at {time.strftime("%I:%M:%S")}')
            time.sleep(3)

        else:
            shared_memory['email_queue'].put(email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("Failed to enter raffle with account. Adding account back to queue.")


def send_raffle_entry_request(session, entry, shared_memory):
    email = entry['email']

    proxy = random.choice(shared_memory['proxies'])

    data = (
        ("token", entry['token']),
    )

    # session.headers.update(
    #     {
    #         'content-type': 'application/x-www-form-urlencoded',
    #         'origin': 'https://www.nakedcph.com',
    #         'referer': 'https://www.nakedcph.com/en/778/raffle-nike-dunk-low-sp-cu1726-101-fcfs-raffle',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'cross-site',
    #         'sec-fetch-user': '?1'
    #     }
    # )

    try:
        response = session.get(
            url="https://app.rule.io/subscriber/optIn",
            params=data,
            proxies=proxy,
            allow_redirects=False,
            timeout=10
        )


    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, Exception) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if str(session.get_redirect_target(response)) == 'https://www.nakedcph.com/en/775/you-are-now-registered-for-our-fcfs-raffle':
        success = True
    else:
        success = False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.text))
        print('  Status - ' + str(response.status_code))

    return success


def email_already_confirmed(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/nakednew/Naked_' + NAKED_RAFFLE_NAME + '_confirmations.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_email_to_file(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/nakednew/Naked_' + NAKED_RAFFLE_NAME + '_confirmations.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + '\n')


def shutdown():
    discord_webhook.raffle_entry_complete(site="Naked Confirmations", raffle=NAKED_RAFFLE_NAME, confirmation=True)
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
