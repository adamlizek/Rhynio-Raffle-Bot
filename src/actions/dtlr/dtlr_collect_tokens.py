import config as CONFIG
import time
import imaplib
import email
import re
import portalocker
import logging
from bs4 import BeautifulSoup


DTLR_RAFFLE_NAME = ''
GMAIL_EMAIL = ''
GMAIL_PASSWORD = ''


def init():
    logging.info('Beginning Token Collection...')

    return {
        'None': 'None'
    }


def run(stop_flag, shared_memory):
    raffle = DTLR_RAFFLE_NAME
    FROM_EMAIL = GMAIL_EMAIL
    FROM_PWD = GMAIL_PASSWORD
    SMTP_SERVER = "imap.gmail.com"
    SMTP_PORT = 993

    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL, FROM_PWD)
        mail.select('inbox')
        type, data = mail.search(None, 'UNSEEN')
        mail_ids = data[0]

        id_list = mail_ids.split()

        if len(id_list) == 0:
            print('No unread emails present! Trying again.')
            logging.info('No unread emails present! Trying again.')
            time.sleep(2)
        else:
            id_list.reverse()

        count = 0
        for id in id_list:
            typ, data = mail.fetch(str(int(id)), '(RFC822)' )

            for response_part in data:
                if not stop_flag.is_set():
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1].decode())

                        email_from = msg['from']
                        email_to = msg['to']

                        email_subject = msg['subject']
                        if 'one more step' in email_subject and 'donotreply@dtlr.com' in email_from:
                            print('DTLR Email Found for ' + email_to)
                            logging.info('DTLR Email Found for ' + email_to)
                            count = 0

                        else:
                            print('Email skipped - ' + email_subject)
                            print(email_from)

                            count += 1
                            if count == 20:
                                logging.info('20 Emails Skipped!')
                                count = 0

                            continue

                        if msg.is_multipart():
                            for payload in msg.get_payload():
                                continue


                        else:
                            # print(base64.b64decode(msg.get_payload()))
                            #raw_email = data[0][1]

                            soup = BeautifulSoup(str(data), features="html.parser")

                            for a in soup.find_all("a", string='Verify Email', href=True):
                                print("Found the URL:", a['href'])
                                url = a['href']
                            #print(soup.find("a", string='Verify Email'))
                            #print(soup)

                            parsed_url = url.replace("\\r", '')
                            parsed_url = parsed_url.replace('3D"', '')
                            parsed_url = parsed_url.replace("\\n", '')
                            parsed_url = parsed_url.replace('=', '')
                            parsed_url = parsed_url.replace('"', '')
                            token = parsed_url.replace('http://email.ecommail.dtlr.com/c/', '')

                            print('[Token] - ' + token)

                            data = {
                                "token": token,
                                "to": email_to
                            }

                            write_token_to_file(data)

        return True

    except Exception as e:
        print('Error ' + str(e))
        logging.info('[Error] - Could not login to Gmail!')


def find(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


def write_token_to_file(data):
    FILE_PATH = CONFIG.ROOT + '/output/dtlr/DTLR_' + DTLR_RAFFLE_NAME + '_tokens.txt'

    with open(FILE_PATH, 'a+') as file:
        portalocker.lock(file, portalocker.LOCK_EX)
        file.write(
            data['to'] + ":" +
            data['token'] + "\n"
        )
