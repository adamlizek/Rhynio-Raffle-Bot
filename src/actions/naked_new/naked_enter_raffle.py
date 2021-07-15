from src.handlers import captcha_handler, proxy_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils, address_api
import config as CONFIG
import queue
import requests
import random
import time
import os
import logging
import threading
from src.utils import faker_generator

from bs4 import BeautifulSoup
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ProxyError
from http.client import RemoteDisconnected

'''
NAKED ENTER RAFFLE CONFIG
'''
NAKED_RAFFLE_URL = 'https://app.rule.io/subscriber-form/subscriber'
NAKED_RAFFLE_WEBPAGE = ''
NAKED_RAFFLE_NAME = ''
NAKED_RAFFLE_COUNTRY = ''
NAKED_RAFFLE_NEWSLETTER = 'Yes'
NAKED_ENTRY_DELAY = 30
NAKED_CAPTCHA_DATA_SITE_KEY = '6LfbPnAUAAAAACqfb_YCtJi7RY0WkK-1T4b9cUO8'
NAKED_CAPTCHA_URL = 'https://www.nakedcph.com/auth/view?op=register'
NAKED_OVERWRITE_ADDRESS = False

NAKED_ENTRY_LEVEL = 2 # Level 1 = Login, Navigate, Enter
                      # Level 2 = Navigate, Enter
                      # Level 3 = Enter

NAKED_RAFFLE_TAGS = ''
NAKED_RAFFLE_TOKEN = ''

def init():
    logging.info("Beginning Raffle Entry...")
    print("Beginning Raffle Entry...\n")

    account_queue = None
    with open(CONFIG.ROOT + '/output/accounts/naked_accounts.txt', 'r') as file:
        accounts = list(file.read().split())
        account_queue = queue.Queue()
        [account_queue.put(a) for a in accounts]

    area_codes = None
    with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
        area_codes = list(file.read().splitlines())

    proxies = proxy_handler.get_proxy_list()

    instagram_followers = None
    with open(CONFIG.ROOT + '/data/social_media/naked_instagram.txt', 'r') as file:
        instagram_followers = list(file.read().splitlines())

    return {
        'account_queue': account_queue,
        'instagrams': instagram_followers,
        'area_codes': area_codes,
        'proxies': proxies,
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['account_queue'].empty():
        unparsed_account = shared_memory['account_queue'].get()

        result_from_parsing = [x.strip() for x in unparsed_account.split(':')]
        account = {
            'email': result_from_parsing[0],
            'password': result_from_parsing[1],
            'first_name': result_from_parsing[2],
            'last_name': result_from_parsing[3]
        }

        if account_already_entered(account['email']):
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

        reused_address, address, instagram = generate_address(account['email'])

        if instagram is None:
            instagram = random.choice(shared_memory['instagrams'])

        successfully_entered = send_raffle_entry_request(account, session, proxy, address, instagram)

        if successfully_entered:
            write_account_to_file(account['email'], proxy)
            discord_webhook.raffle_to_webhook(account, site="Naked", raffle=NAKED_RAFFLE_NAME)
            email = account['email']

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')

            if not reused_address:
                log_data.log_naked_address(email, address, instagram)

            if CONFIG.LOG_ENTRIES:
                log_data.log_entry_data(site="NAKED",
                                        raffle=NAKED_RAFFLE_NAME,
                                        email=email,
                                        proxy=proxy_handler.parse_into_default_form(proxy),
                                        delay=NAKED_ENTRY_DELAY,
                                        country=NAKED_RAFFLE_COUNTRY
                                        )
            session.close()

        else:
            shared_memory['account_queue'].put(unparsed_account)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            time.sleep(1)
            session.close()


def send_raffle_entry_request(account, session, proxy, address, instagram):
    session.proxies = proxy

    if NAKED_ENTRY_LEVEL == 1:
        session, success = send_login_request(account, session, proxy)

        if success is False:
            print('Login Failed')
            return False
        else:
            if CONFIG.DEBUG_MODE:
                print('Login Success!')

    '''
    Navigation Request
    '''
    new_session = cloudscraper_utils.create_scraper()
    new_session.proxies = proxy

    if NAKED_ENTRY_LEVEL == 1:
        new_session.headers.update(
            {
                'User-Agent': session.headers['User-Agent'],
            }
        )
        new_session.cookies = session.cookies

    if NAKED_ENTRY_LEVEL < 3:
        try:
            navigation = new_session.get(
                url=NAKED_RAFFLE_WEBPAGE,
                timeout=20
            )
        except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
            print("Proxy Error Handled - " + str(e))
            print(proxy_handler.parse_into_default_form(proxy))
            return False

        try:
            soup = BeautifulSoup(navigation.text, 'html.parser')
            tags = soup.find('input', {'name': 'tags[]'}).get('value')
            token = soup.find('input', {'name': 'token'}).get('value')

        except:
            print("Error: " + proxy['https'] + " is bad!")
            logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
            return False

        try:
            navigation = new_session.post(
                url=NAKED_RAFFLE_WEBPAGE,
            )
        except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
            print("Proxy Error Handled - " + str(e))
            print(proxy_handler.parse_into_default_form(proxy))
            return False

        if CONFIG.DEBUG_MODE:
            print('Navigation Debug - ' + str(navigation.content))
            print('  Status - ' + str(navigation.status_code))

    else:
        tags = NAKED_RAFFLE_TAGS
        token = NAKED_RAFFLE_TOKEN

    try:
        ip_address = requests.get(
            url='https://api.ipify.org/',
            proxies=proxy,
            timeout=20
        ).text
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError):
        print("Proxy Error Handled")
        return False

    captcha_token = captcha_handler.handle_captcha(NAKED_RAFFLE_WEBPAGE, '6LfbPnAUAAAAACqfb_YCtJi7RY0WkK-1T4b9cUO8', invisible=True)
    if len(captcha_token) < 10:
        print('Captcha Failed')
        return False

    data = {
        "tags[]": tags,
        "token": token,
        "rule_email": account['email'],
        "fields[Raffle.Instagram Handle]": instagram,
        "fields[Raffle.Phone Number]": address['phone_number'],
        "fields[Raffle.First Name]": account['first_name'],
        "fields[Raffle.Last Name]": account['last_name'],
        "fields[Raffle.Shipping Address]": address["address_1"],
        "fields[Raffle.Postal Code]": address["zip"],
        "fields[Raffle.City]": address["city"],
        "fields[Raffle.Country]": address["country"],
        "fields[Raffle.Signup Newsletter]": 'on',
        "fields[SignupSource.ip]": ip_address,
        "fields[SignupSource.useragent]": new_session.headers['User-Agent'],
        'language': 'sv',
        'g-recaptcha-response': captcha_token
    }

    new_session.headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.nakedcph.com',
        'Referer': 'https://www.nakedcph.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': new_session.headers['User-Agent']
    })

    try:
        response = new_session.post(url=NAKED_RAFFLE_URL,
                                    allow_redirects=False,
                                    data=data,
                                    timeout=30)
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
        print("Proxy Error Handled - " + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print('Raffle Entry Debug - ' + str(response.content))
        print('  Status - ' + str(response.status_code))
        print('  Redirect - ' + str(session.get_redirect_target(response)))

    if str(session.get_redirect_target(response)) == 'https://www.nakedcph.com/en/772/your-registration-for-our-fcfs-was-successful':
        success = True
    else:
        success = False

    return success


def send_login_request(account, session, proxy):
    # populate data for login request
    '''
    Initial Get Request
    '''
    session.proxies = proxy

    try:
        initial = session.get(
            url='https://www.nakedcph.com/en/auth/view',
            timeout=10
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, RuntimeError, OSError, Exception) as e:
        print("Proxy Error Handled - " + str(e))
        print(proxy_handler.parse_into_default_form(proxy))
        return session, False

    if CONFIG.DEBUG_MODE:
        print('[1] Login Debug - ' )#+ str(initial.content))
        print('  Status - ' + str(initial.status_code))

    try:
        ANTI_CSRF_TOKEN = session.cookies.get_dict()['AntiCsrfToken']

    except KeyError:
        print("Error: " + proxy['https'] + " is bad!")
        logging.info("[" + threading.currentThread().getName() + "] " + "Error: " + proxy['https'] + " is bad!")
        return session, False

    '''
    Login Post Request
    '''

    # populate data for login request
    session.headers.update(
        {
            'Referer': 'https://www.nakedcph.com/en/auth/view',
            'Origin': 'https://www.nakedcph.com',
            'X-Anticsrftoken': ANTI_CSRF_TOKEN,
            'X-Requested-With': 'XMLHttpRequest',
        }
    )

    login_data = {
        '_AntiCsrfToken': ANTI_CSRF_TOKEN,
        'action': 'login',
        'email': account['email'],
        'g-recaptcha-response': captcha_handler.handle_captcha(NAKED_CAPTCHA_URL,
                                                               NAKED_CAPTCHA_DATA_SITE_KEY),
        'password': account['password']
    }

    # perform login request
    try:
        login_request = session.post(
            url='https://www.nakedcph.com/en/auth/submit',
            data=login_data,
            timeout=20
        )
    except (MaxRetryError, ProxyError, RemoteDisconnected, OSError, Exception) as e:
        print(e)
        print("Proxy Error Handled")
        return session, False


    if CONFIG.DEBUG_MODE:
        print('[2] Account Login Debug - ')# + str(login_request.content))
        print('  Status - ' + str(login_request.status_code))

    if login_request.status_code == 500:
        if "ReCaptchaFailed" in login_request.text:
            return session, False

    if login_request.text == '{"Response":{"Success":true,"Action":"Login"},"StatusCode":0,"Status":"OK"}':
        success = True
    else:
        success = False

    return session, success


def account_already_entered(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/nakednew/Naked_' + NAKED_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'a+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return account in file.read()


def write_account_to_file(email, proxy):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/nakednew/Naked_' + NAKED_RAFFLE_NAME + '_entries.txt'
    proxy = proxy_handler.parse_into_default_form(proxy)

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'a+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + ":" + proxy + '\n')


def generate_address(email):
    logged_address = log_data.check_for_naked_address(email)

    if logged_address and not NAKED_OVERWRITE_ADDRESS:
        return True, logged_address, logged_address['instagram']
    else:
        country = NAKED_RAFFLE_COUNTRY

        if country == 'Random':
            country = random.choice(['Denmark',
                                     'United Kingdom', 'Germany',
                                     'France', 'Spain', 'Portugal', 'Romania'])

        address_info = faker_generator.generate_naked_address(country)

        if not CONFIG.USE_FAKER and country == 'United States':
            real_address = address_api.get_address('US')
            address_info['address_1'] = real_address['address_1']
            address_info['city'] = real_address['city']
            address_info['zip'] = real_address['postcode']

        address_info['phone_number'] = address_info['phone_number'].replace('+', '')

        if CONFIG.DEBUG_MODE:
            print(address_info)

        return False, address_info, None


def shutdown():
    discord_webhook.raffle_entry_complete("Naked", NAKED_RAFFLE_NAME)
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")

