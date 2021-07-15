from src.handlers import captcha_handler, proxy_handler, email_handler
from src.utils import discord_webhook, log_data, cloudscraper_utils
import config as CONFIG
import random
import time
import os
import json
from random import randint
import logging
import threading
from src.utils import faker_generator
from faker import Faker


# these will be populated by DB
B4B_RAFFLE_NAME = ''
B4B_RAFFLE_URL = ''
B4B_TOKEN = ''
B4B_ID_RAFFLE = ''
B4B_VARIANTS = []

B4B_DATA_SITE_KEY = '6LcpBD0UAAAAALwqETJkSSuQZYcavdDKu1sy_XPN'

B4B_PLUSTRICK_ENABLED = False
B4B_GMAIL = ''

B4B_CATCHALL_ENABLED = False
B4B_CATCHALL = ''

def init():
    logging.info("Beginning Raffle Entry...")
    print("Beginning Raffle Entry...\n")

    email_queue = email_handler.get_email_queue()
    proxies = proxy_handler.get_proxy_list()

    instagrams = None
    with open(CONFIG.ROOT + '/data/social_media/b4b_instagram.txt', 'r') as file:
        instagrams = list(file.read().splitlines())

    return {
        'proxies': proxies,
        'email_queue': email_queue,
        'instagrams': instagrams
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['email_queue'].empty():
        fake = Faker('en_US')

        name = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name()
        }

        if B4B_PLUSTRICK_ENABLED:
            result_from_parsing = [x.strip() for x in B4B_GMAIL.split('@')]
            email_split = result_from_parsing[0]
            email = email_split + "+" + str(random.randint(0, 99999)) + "@gmail.com"

        elif B4B_CATCHALL_ENABLED:
            email = name['first_name'] + name['last_name'] + str(randint(10, 99)) + '@' + B4B_CATCHALL

        else:
            unparsed_email = shared_memory['email_queue'].get()
            email = unparsed_email.get_email()
            if unparsed_email.nameEnabled():
                name = {
                    'first_name': unparsed_email.get_first_name(),
                    'last_name': unparsed_email.get_last_name()
                }

        if account_already_entered(email):
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
        successfully_entered = send_raffle_entry_request(email, session, proxy, name, shared_memory)

        if successfully_entered:
            write_account_to_file(email)
            discord_webhook.raffle_to_webhook(email, site="B4B", raffle=B4B_RAFFLE_NAME)

            print(f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')
            logging.info("[" + threading.currentThread().getName() + "] " + f'Successfully entered {email} at {time.strftime("%I:%M:%S")}')

            if CONFIG.LOG_ENTRIES:
                log_data.log_entry_data(site="B4B",
                                        raffle=B4B_RAFFLE_NAME,
                                        email=email,
                                        proxy=proxy_handler.parse_into_default_form(proxy),
                                        delay='Captcha',
                                        country='France'
                                        )

            session.close()

        else:
            if not B4B_CATCHALL_ENABLED and not B4B_PLUSTRICK_ENABLED:
                shared_memory['email_queue'].put(unparsed_email)
            print("Failed to enter raffle with account. Adding account back to queue.")
            if CONFIG.SHOW_FAILURE:
                logging.info("[" + threading.currentThread().getName() + "] " +
                             "Failed to enter raffle with account. Adding account back to queue.")
            time.sleep(1)
            session.close()


def send_raffle_entry_request(email, session, proxy, name, shared_memory):

    try:
        get_req = session.get(
            url=B4B_RAFFLE_URL,
            proxies=proxy,
            timeout=60
        )
    except Exception as e:
        print('Proxy Error - ' + str(e))
        return False

    if CONFIG.DEBUG_MODE:
        print(f"GET REQ [{get_req.status_code}]: {get_req.content}")

    time.sleep(10)

    r = session.post(url="https://www.basket4ballers.com/sbbi/",
                     data={
                         "bhvmsg": "112a60a124a100a42a59a42a41a32a124a111a107a43a41a52a124a37a",
                         "cdmsg": "49a117a58a63a44a117a40a38a45a48a122a114a115a102a61a32a48a32a114a43a58a53a55a103a32a113a47a40a36a36a34a32a41a36a36a106a32a45a51a37a54a58a126a34a126a57a32a111a37a40a44a47a56a107a123a123a105a118a122a110a115a113a115a126a115a121a110a113a118a126a113a115a125a",
                         "femsg": "1",
                         "futgs": "",
                         "glv": "119a",
                         "jsdk": "GejWfbk",
                         "lext": "28a117a102a103a27a",
                         "sdrv": "0",
                     }
                     )

    print(r.status_code)
    print(r.content)


    session.headers.update(
        {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.basket4ballers.com',
            'referer': B4B_RAFFLE_URL,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }
    )

    address = generate_address()
    last_name = name['last_name']
    first_name = name['first_name']

    facebook_account = (first_name + last_name).lower()
    instagram_account = random.choice(shared_memory['instagrams'])

    raffleRegistrationInfo = {
        'lastname': last_name,
        'firstname': first_name,
        'email': email,
        'company': '',
        'address1': address['address_1'],
        'address2': '',
        'postcode': address['zip'],
        'city': address['city'],
        'id_country': '8',
        'id_state': '313',
        'phone': address['phone_number'],
        'id_facebook': facebook_account,
        'id_instagram': instagram_account,
        'id_attribute_choice': random.choice(B4B_VARIANTS),  # SIZE
        'newsletter': '1',
        'age': '1',
        'id_raffle': B4B_ID_RAFFLE,
        'token': B4B_TOKEN,
    }

    data = {
        'action': 'submitRaffleRegistration',
        'ajax': 'true',
        'g-recaptcha-response': captcha_handler.handle_captcha(B4B_RAFFLE_URL,
                                                               B4B_DATA_SITE_KEY),
        'raffleRegistration': str(json.dumps(raffleRegistrationInfo)),
        'token': B4B_TOKEN
    }

    try:
        submit_req = session.post(
            url='https://www.basket4ballers.com/modules/b4b_raffle/ajax/' + '?rand=' + str(int(time.time())),
            data=data,
            proxies=proxy,
            timeout=60
        )
    except Exception as e:
        print(e)
        return False

    if CONFIG.DEBUG_MODE:
        print(submit_req.status_code)
        print(submit_req.content)

    if str(submit_req.content) == 'b\'{"errors":[]}\'':
        success = True
    elif str(submit_req.content) == 'b\'{"errors":["Une inscription est d&eacute;j&agrave; enregistr&eacute;e avec cet e-mail"]}\'':
        print('Duplicate Email')
        success = True
    else:
        success = False

    return success


def account_already_entered(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/b4b_' + B4B_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'a+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return email in file.read()


def write_account_to_file(email):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/b4b_' + B4B_RAFFLE_NAME + '_entries.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'a+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(email + '\n')


def generate_address():
    address_info = faker_generator.generate_naked_address('US')

    return address_info


def shutdown():
    discord_webhook.raffle_entry_complete("Basket4Ballers", B4B_RAFFLE_NAME)
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
    logging.info("There are no more accounts remaining to enter raffles! Shutting down.")

