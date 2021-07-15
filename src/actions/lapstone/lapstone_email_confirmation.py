from src.handlers import captcha_handler, proxy_handler, selenium_handler
from src.utils import discord_webhook, cloudscraper_utils
import config as CONFIG
import queue
import requests
import random
import time
import json
import os
import logging
from enum import Enum
import threading

from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected


class status(Enum):
    PROXY_FAILED = 1
    CAPTCHA_FAILED = 2
    COOKIE_FAILED = 3
    SUCCESS = 4


'''
Lapstone Raffle Confirmation
'''
LAPSTONE_CAPTCHA_DATA_SITE_KEY = '6LcN9xoUAAAAAHqSkoJixPbUldBoHojA_GCp6Ims'
LAPSTONE_CAPTCHA_URL = 'https://lapstoneandhammer.us10.list-manage.com/subscribe/confirm'

LAPSTONE_RAFFLE_NAME = ''
LAPSTONE_RAFFLE_U = ''
LAPSTONE_RAFFLE_ID = ''
LAPSTONE_DELAY = 15


def init():
    print("Beginning Raffle Confirmations...\n")
    logging.info("Beginning Raffle Confirmations...")


    TOKEN_FILE_PATH = CONFIG.ROOT + '/output/lapstone/Lapstone_' + LAPSTONE_RAFFLE_NAME + '_tokens.txt'

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

        logging.info('[Error] - Token file does not exist! Please run the Lapstone Token Collector First.')
        print('[Error] - Token file does not exist! Please run the Lapstone Token Collector First.')

    cookies = None
    with open(CONFIG.ROOT + '/data/cookies/lapstone_cookies.txt', 'r') as file:
        cookies = list(file.read().split())

    return {
        'email_queue': email_queue,
        'proxies': proxies,
        'cookies': cookies
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        email = shared_memory['email_queue'].get()

        if 'lapstoneandhammer' in email:
            result = email.replace(
                'https://us10.mailchimp.com/mctx/clicks?url=https%3A%2F%2Flapstoneandhammer.us10.list-manage.com%2Fsubscribe%2Fconfirm',
                '')

            # Find the 'e' param
            lower_bound = '%26e%3D'
            upper_bound = '&h='

            result_2 = result[result.rindex(lower_bound): result.rindex(upper_bound)]

            e = result_2.replace(lower_bound, '')
            entry = {
                'email': 'Unknown',
                'e': e
            }

        else:
            result_from_parsing = [x.strip() for x in email.split(':')]
            entry = {
                'email': result_from_parsing[0],
                'e': result_from_parsing[1]
            }

        if email_already_confirmed(entry['e']):
            continue

        scraper = cloudscraper_utils.create_scraper()

        try:
            cookie = random.choice(shared_memory['cookies'])
        except IndexError:
            print('All cookies have been used! Please generate more cookies')
            logging.info('All cookies have been used! Please generate more cookies')
            break

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

        successfully_entered, status = send_raffle_entry_request(scraper, entry, proxy, cookie)

        if successfully_entered:
            write_email_to_file(entry['e'])
            discord_webhook.confirmation_to_webhook(entry['email'], site="Lapstone", raffle=LAPSTONE_RAFFLE_NAME)

            print(f'Successfully confirmed {entry["email"]} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " +f'Successfully confirmed {entry["email"]} at {time.strftime("%I:%M:%S")}')
            scraper.close()
            time.sleep(1)

        else:
            if status == status.COOKIE_FAILED:
                try:
                    shared_memory['cookies'].remove(cookie)
                    if CONFIG.DEBUG_MODE:
                        logging.info("[" + threading.currentThread().getName() + "] " +'Failed: Bad Cookie Removed')

                except ValueError:
                    if CONFIG.DEBUG_MODE:
                        print('Cookie Already Removed')

            shared_memory['email_queue'].put(email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("Failed to enter raffle with account. Adding account back to queue.")

            scraper.close()
            time.sleep(1)

# **** RUN FOR BROWSER BASED ****
# def run(stop_flag, shared_memory):
#     while not stop_flag.is_set() and not shared_memory['url_queue'].empty():
#         url = shared_memory['url_queue'].get()
#
#         if email_already_confirmed(url):
#             continue
#
#         scraper = cloudscraper_utils.create_scraper()
#
#         try:
#             proxy = random.choice(shared_memory['proxies'])
#         except IndexError:
#             print('All proxies have been used! Please enter more proxies')
#             logging.info('All proxies have been used! Please enter more proxies')
#             break
#
#

        # driver = selenium_handler.get_chromedriver(proxy_handler.parse_into_default_form(proxy), user_agent=scraper.headers['User-Agent'])
        #
        # try:
        #     successfully_entered = confirm_via_broswer(driver, url)
        # except Exception:
        #     successfully_entered = False
        #
        # if successfully_entered:
        #     write_email_to_file(url)
        #     print(f'Successfully confirmed url at {time.strftime("%I:%M:%S")}')
        #     logging.info(f'Successfully confirmed url at {time.strftime("%I:%M:%S")}')
        #     scraper.close()
        #     driver.close()
        #     time.sleep(1)
        #
        # else:
        #     shared_memory['url_queue'].put(url)
        #     print("Failed to confirm raffle. Adding back to queue.")
        #     if CONFIG.SHOW_FAILURE:
        #         logging.info("Failed to confirm raffle. Adding back to queue.")
        #     scraper.close()
        #     driver.close()
        #     time.sleep(1)
#
#
# def confirm_via_broswer(driver, url):
#     driver.get(url)
#     captcha_token = captcha_handler.handle_captcha(LAPSTONE_CAPTCHA_URL, LAPSTONE_CAPTCHA_DATA_SITE_KEY)
#     if len(captcha_token) < 10:
#         print('Captcha Failed')
#         return False
#     else:
#         print(captcha_token)
#
#     script = 'document.getElementById("g-recaptcha-response").innerHTML="' + captcha_token + '";'
#     driver.execute_script(script)
#     driver.find_element_by_class_name('formEmailButton').click()
#     time.sleep(3)
#     return True


def send_raffle_entry_request(scraper, entry, proxy, cookie):
    url = 'https://lapstoneandhammer.us10.list-manage.com/subscribe/confirm?u=' + LAPSTONE_RAFFLE_U + '&id=' \
            + LAPSTONE_RAFFLE_ID + '&e=' + entry['e']

    initial_data = (
        ('u', LAPSTONE_RAFFLE_U),
        ('id', LAPSTONE_RAFFLE_ID),
        ('e', entry['e'])
    )

    try:
        response = scraper.get(
            url='https://lapstoneandhammer.us10.list-manage.com/subscribe/confirm',
            params=initial_data,
            proxies=proxy,
            timeout=10
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False, status.PROXY_FAILED

    if CONFIG.DEBUG_MODE:
        print(response.content)
        print(response.status_code)
        print(scraper.cookies)

    abck_cookie = cookie

    scraper.cookies.set_cookie(
        requests.cookies.create_cookie(name='_abck', value=abck_cookie, domain='.list-manage.com'))

    scraper.headers.update = (
        {
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://lapstoneandhammer.us10.list-manage.com',
            'referer': url,
        }
    )

    captcha_token = captcha_handler.handle_captcha(LAPSTONE_CAPTCHA_URL, LAPSTONE_CAPTCHA_DATA_SITE_KEY)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False, status.CAPTCHA_FAILED

    post_data = {
        'e': entry['e'],
        'g-recaptcha-response': captcha_token,
        'id': LAPSTONE_RAFFLE_ID,
        'recaptcha_response_field': 'manual_challenge',
        'u': LAPSTONE_RAFFLE_U
    }

    try:
        response = scraper.post(
            url="https://lapstoneandhammer.us10.list-manage.com/subscribe/confirm",
            data=post_data,
            proxies=proxy,
            timeout=10
        )

    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError) as e:
        print("Proxy Error Handled - " + str(e))
        return False, status.PROXY_FAILED

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.text))
        print('  Status - ' + str(response.status_code))

    print(response.status_code)
    # print(response.text)

    if 'Your subscription to our list has been confirmed' in response.text:
        return True, status.SUCCESS
    elif response.status_code == 406:
        return False, status.COOKIE_FAILED
    else:
        return False, status.CAPTCHA_FAILED
    
def generate_cookie(entry, proxy, session):
    #clear_cookies()
    driver = selenium_handler.get_chromedriver(proxy, user_agent=session.headers['User-Agent'])
    while True:
        driver.get('https://lapstoneandhammer.us10.list-manage.com/subscribe/confirm?u='+LAPSTONE_RAFFLE_U+'&id='+LAPSTONE_RAFFLE_ID+'&e='+entry['e'])
        time.sleep(1)

        cookies_list = driver.get_cookies()
        cookies_dict = {}
        for cookie in cookies_list:
            cookies_dict[cookie['name']] = cookie['value']

        abck_cookie = cookies_dict['_abck']
        if '~0~' not in abck_cookie:
            print('Invalid Cookie!')
            continue
        break

    driver.delete_all_cookies()
    driver.close()

    print(abck_cookie)
    return abck_cookie


def email_already_confirmed(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/lapstone/Lapstone_' + LAPSTONE_RAFFLE_NAME + '_confirmed.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_email_to_file(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/lapstone/Lapstone_' + LAPSTONE_RAFFLE_NAME + '_confirmed.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + '\n')


def shutdown():
    discord_webhook.raffle_entry_complete(site="Lapstone Confirmations", raffle=LAPSTONE_RAFFLE_NAME, confirmation=True)
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
