from src.handlers import captcha_handler, proxy_handler
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


ATMOS_RAFFLE_NAME = ''
ATMOS_DATA_SITEKEY = '6LcES6sZAAAAACGrj8rrJm13isYkVke0iBaZwtaF'


def init():
    print("Beginning Raffle Confirmations...\n")
    logging.info("Beginning Raffle Confirmations...")

    URL_FILE_PATH = CONFIG.ROOT + '/output/atmos/Atmos_' + ATMOS_RAFFLE_NAME + '_links.txt'

    proxies = proxy_handler.get_proxy_list()
    try:
        url_queue = None
        with open(URL_FILE_PATH, 'r') as file:
            urls = list(file.read().split())
            url_queue = queue.Queue()
            [url_queue.put(a) for a in urls]
    except IOError:
        if not os.path.exists(CONFIG.ROOT + '/output/atmos/Atmos_' + ATMOS_RAFFLE_NAME + '_links.txt'):
            file = open(CONFIG.ROOT + '/output/atmos/Atmos_' + ATMOS_RAFFLE_NAME + '_links.txt', 'w+')
            file.close()

        logging.info('[Error] - Token file does not exist! Please run the Atmos Token Collector First.')
        print('[Error] - Token file does not exist! Please run the Atmos Token Collector First.')

    return {
        'url_queue': url_queue,
        'proxies': proxies,
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['url_queue'].empty():
        url = shared_memory['url_queue'].get()

        if email_already_confirmed(url):
            continue

        scraper = cloudscraper_utils.create_scraper()

        try:
            proxy = random.choice(shared_memory['proxies'])
            shared_memory['proxies'].remove(proxy)
        except IndexError:
            print('All proxies have been used! Please enter more proxies')
            logging.info('All proxies have been used! Please enter more proxies')
            break

        successfully_entered = send_raffle_entry_request(scraper, proxy, url)

        if successfully_entered:
            write_email_to_file(url)
            print(f'Successfully confirmed url at {time.strftime("%I:%M:%S")}')
            logging.info(f'Successfully confirmed url at {time.strftime("%I:%M:%S")}')
            scraper.close()
            time.sleep(1)

        else:
            shared_memory['url_queue'].put(url)
            print("Failed to confirm raffle. Adding back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("Failed to confirm raffle. Adding back to queue.")
            scraper.close()
            time.sleep(1)


def send_raffle_entry_request(scraper, proxy, url):
    try:
        response = scraper.get(
            url=url,
            proxies=proxy,
            timeout=10
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print(response.content)
        print(response.status_code)
        print(scraper.cookies)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'https://releases.atmosusa.com',
        'Referer': 'https://releases.atmosusa.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': scraper.headers['User-Agent'],
        'dnt': '1'
    }

    captcha_token = captcha_handler.handle_captcha('https://releases.atmosusa.com/entry', ATMOS_DATA_SITEKEY)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False

    split_string = url.split("/")

    post_data = {
        'verificationCode': split_string[-1],
        'recaptcha': captcha_token
    }

    try:
        response = scraper.post(
            url="https://stage-ubiq-raffle-strapi-be.herokuapp.com/entries/verify",
            json=post_data,
            headers=headers,
            proxies=proxy,
            timeout=15
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.text))
        print('  Status - ' + str(response.status_code))

    if response.ok:
        success = True
    else:
        success = False

    return success


def email_already_confirmed(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/atmos/Atmos_' + ATMOS_RAFFLE_NAME + '_confirmed.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_email_to_file(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/atmos/Atmos_' + ATMOS_RAFFLE_NAME + '_confirmed.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + '\n')


def shutdown():
    discord_webhook.raffle_entry_complete(site="Atmos Confirmations", raffle=ATMOS_RAFFLE_NAME, confirmation=True)
    logging.info("There are no more accounts remaining to confirm! Shutting down.")
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
