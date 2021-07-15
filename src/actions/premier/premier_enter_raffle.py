from src.handlers import proxy_handler, selenium_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils
import config as CONFIG
import queue
from random import randint
import random
import time
import json
import os
import logging
import threading
from selenium.common.exceptions import ElementClickInterceptedException


PREMIER_RAFFLE_NAME = ''
PREMIER_RAFFLE_ID = ''
PREMIER_LOGIN_CAPTCHA = False

PREMIER_CUSTOMZIP_ENABLED = False
PREMIER_CUSTOMZIP = ''


def init():
    print("Beginning Raffle Entry...\n")
    logging.info("Beginning Raffle Entry...")

    account_queue = None
    with open(CONFIG.ROOT + '/output/accounts/premier_accounts.txt', 'r') as file:
        accounts = list(file.read().split())
        account_queue = queue.Queue()
        [account_queue.put(a) for a in accounts]

    zip_codes = None
    with open(CONFIG.ROOT + '/data/info/cities.txt', 'r') as file:
        zip_codes = list(file.read().splitlines())

    proxies = None
    with open(CONFIG.ROOT + '/data/proxies/proxy_lists.json', 'r') as json_file:
        data = json.load(json_file)

        list_id = 0
        while list_id < len(data['proxies']):
            if data['proxies'][list_id]['list_name'] == CONFIG.PROXY_LIST_NAME:
                break

        unformatted_proxy_list = data['proxies'][list_id]['proxies']
        proxies = proxy_handler.parse_into_request_format(unformatted_proxy_list)

    sizes = ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12']

    return {
            'account_queue': account_queue,
            'zip_codes': zip_codes,
            'proxies': proxies,
            'sizes': sizes,
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['account_queue'].empty():
        unparsed_account = shared_memory['account_queue'].get()

        result_from_parsing = [x.strip() for x in unparsed_account.split(':')]
        account = {
            'email': result_from_parsing[0],
            'password': result_from_parsing[1],
            'first_name': result_from_parsing[2],
            'last_name': result_from_parsing[3],
            'zip': random.choice(shared_memory['zip_codes'])
        }

        if PREMIER_CUSTOMZIP_ENABLED:
            split_zips = [x.strip() for x in PREMIER_CUSTOMZIP.split(',')]
            zip_code = random.choice(split_zips)
            account['zip'] = zip_code
            if CONFIG.DEBUG_MODE:
                print(zip_code)

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

        # each thread should have its own session
        session = cloudscraper_utils.create_scraper()

        successfully_entered = send_raffle_entry_request(account, session, proxy)

        if successfully_entered:
            write_account_to_file(account)
            discord_webhook.raffle_to_webhook(account, site="Premier", raffle=PREMIER_RAFFLE_NAME, zip_code=account['zip'])
            email = account['email']

            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            session.close()

            if CONFIG.LOG_ENTRIES:
                log_data.log_entry_data(site="Premier",
                                        raffle=PREMIER_RAFFLE_NAME,
                                        email=email,
                                        proxy=proxy_handler.parse_into_default_form(proxy),
                                        delay="null",
                                        country=account['zip']
                                        )
        else:
            shared_memory['account_queue'].put(unparsed_account)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            session.close()


def send_login_request(account, session, proxy):
    # retrieving main chunk url
    chunkUrlReq = session.get(
        'https://niftygateway.com'
    )

    chunkUrlIndex = str(chunkUrlReq.content).find("src=\"/static/js/main")
    container = str(chunkUrlReq.content)[chunkUrlIndex:chunkUrlIndex + 50]
    splits = container.split('\"')

    chunkUrlSuffix = splits[1]
    chunkUrl = 'https://niftygateway.com' + chunkUrlSuffix

    # Retrieving client id
    clientIdReq = session.get(chunkUrl)

    index = str(clientIdReq.content).find("REACT_APP_CLIENT_ID")

    container = str(clientIdReq.content)[index:index + 100]
    splits = container.split('\"')

    client_id = splits[1]

    # Getting Bearer token
    data = {
        'client_id': client_id,
        'password': account['password'],
        'username': account['email'],
        'grant_type': 'password',
    }

    resp = session.post(
        url='https://api.niftygateway.com/o/token/',
        data=data
    )

    if '"access_token": "' in str(resp.content):
        saved_auth_token = resp.json()['access_token']
        print(session.cookies)

        session.headers.update({
            'Authorization': 'Bearer ' + saved_auth_token
        })
        return session, True

    else:
        return session, False

def send_raffle_entry_request(account, session, proxy):
    session, success = send_login_request(account, session, proxy)

    if success == False:
        print('Login Failed')
        return False

    driver = selenium_handler.get_chromedriver(proxy_handler.parse_into_default_form(proxy), session.headers['user-agent'])
    # # passing the cookie of the response to the browser
    driver.get('https://thepremierstore.com/')

    try:
        for cookie in session.cookies:
            driver.add_cookie({'name': str(cookie.name), 'value': str(cookie.value), 'domain': str(cookie.domain)})
    except Exception:
        if CONFIG.DEBUG_MODE:
            print("Cookie Error!")
            return False

    url = 'https://thepremierstore.com/pages/' + PREMIER_RAFFLE_ID + '?t=' + str(int(time.time()))
    driver.get(url)

    while True:
        try:
            while True:
                try:
                    # Online
                    online_element = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/div[4]/div[3]/div[2]/div/div/div[1]') #.click()
                    driver.execute_script("arguments[0].click();", online_element)
                    time.sleep(1)
                    break
                except ElementClickInterceptedException:
                    driver.find_element_by_xpath('//*[@id="' + PREMIER_RAFFLE_ID + '"]/div[17]/div/div/div/button/img').click()
            while True:
                try:
                    # Size
                    size_element = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/div[4]/div[4]/div[2]/div/div[' + str(randint(2, 19)) + ']')#.click()
                    driver.execute_script("arguments[0].click();", size_element)
                    time.sleep(1)
                    break
                except ElementClickInterceptedException:
                    driver.find_element_by_xpath('//*[@id="' + PREMIER_RAFFLE_ID + '"]/div[17]/div/div/div/button/img').click()

            while True:
                try:
                    # Zip
                    driver.find_element_by_xpath('//*[@id="zip"]').send_keys(account['zip'])
                    time.sleep(1)
                    break
                except ElementClickInterceptedException:
                    driver.find_element_by_xpath('//*[@id="bj-dunk-low"]/div[17]/div/div/div/button/img').click()

            while True:
                try:
                    # I Agree
                    agree_element = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/div[4]/div[5]/div[2]/div[2]/div[1]/input')#.click()
                    driver.execute_script("arguments[0].click();", agree_element)
                    time.sleep(1)
                    break
                except ElementClickInterceptedException:
                    driver.find_element_by_xpath('//*[@id="' + PREMIER_RAFFLE_ID + '"]/div[17]/div/div/div/button/img').click()

            while True:
                try:
                    # Submit
                    submit_element = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/div[4]/div[5]/div[2]/div[2]/div[2]/div')#.click()
                    driver.execute_script("arguments[0].click();", submit_element)
                    time.sleep(5)
                    break
                except ElementClickInterceptedException:
                    driver.find_element_by_xpath('//*[@id="' + PREMIER_RAFFLE_ID + '"]/div[17]/div/div/div/button/img').click()

            break
        except ElementClickInterceptedException:
            driver.find_element_by_xpath('//*[@id="' + PREMIER_RAFFLE_ID + '"]/div[17]/div/div/div/button/img').click()

            break
        except Exception as e:
            time.sleep(1)

    driver.close()
    return True


def account_already_entered(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Premier_' + PREMIER_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return account in file.read()


def write_account_to_file(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/Premier_' + PREMIER_RAFFLE_NAME + '.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(account['email'] + '\n')

def shutdown():
    discord_webhook.raffle_entry_complete("Premier", PREMIER_RAFFLE_NAME)
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")
