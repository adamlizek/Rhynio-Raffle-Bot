from src.handlers import selenium_handler, proxy_handler
from src.utils import cloudscraper_utils
import config as CONFIG
import random
import time
import json
import logging
import threading

cookie_file_path = CONFIG.ROOT + '/data/cookies/lapstone_cookies.txt'

LAPSTONE_RAFFLE_U = '3dd44920c3e2410d48d7462fc'
LAPSTONE_RAFFLE_ID = '06e4acc890'

def init():
    print("Beginning Cookie Generation...\n")
    logging.info("Beginning Cookie Generation...")

    clear_cookies()

    proxies = None
    with open(CONFIG.ROOT + '/data/proxies/proxy_lists.json', 'r') as json_file:
        data = json.load(json_file)

        list_id = 0
        while list_id < len(data['proxies']):
            if data['proxies'][list_id]['list_name'] == CONFIG.PROXY_LIST_NAME:
                break

        unformatted_proxy_list = data['proxies'][list_id]['proxies']
        proxies = proxy_handler.parse_into_request_format(unformatted_proxy_list)

    return {
        'proxies': proxies,
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set():
        session = cloudscraper_utils.create_scraper()

        proxy = random.choice(shared_memory['proxies'])
        driver = selenium_handler.get_chromedriver(proxy_handler.parse_into_default_form(proxy), user_agent=session.headers['User-Agent'])

        invalid_cookies = 0
        while True:
            driver.get('https://lapstoneandhammer.us10.list-manage.com/subscribe/confirm?u='+LAPSTONE_RAFFLE_U+'&id='+LAPSTONE_RAFFLE_ID+'&e=379ef257be')
            time.sleep(1)

            cookies_list = driver.get_cookies()
            cookies_dict = {}
            for cookie in cookies_list:
                cookies_dict[cookie['name']] = cookie['value']

            try:
                abck_cookie = cookies_dict['_abck']
            except KeyError:
                driver.delete_all_cookies()
                continue

            if '~0~' not in abck_cookie:
                logging.info("[" + threading.currentThread().getName() + "] " + 'Invalid Cookie!')
                invalid_cookies += 1
                driver.delete_all_cookies()

                if invalid_cookies == 10:
                    break
                else:
                    continue

            write_cookie(abck_cookie)
            driver.delete_all_cookies()
            logging.info("[" + threading.currentThread().getName() + "] " + 'Cookie Genned!')

        driver.close()
        session.close()


def clear_cookies():
    open(cookie_file_path, 'w+').close()


def write_cookie(cookie):
    with open(cookie_file_path, 'a+') as file:
        file.write(cookie + '\n')
