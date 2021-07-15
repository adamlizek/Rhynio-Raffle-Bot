import config as CONFIG
import time
import imaplib
import email
import re
import portalocker
import logging
import os

NAKED_RAFFLE_NAME = ''
NAKED_SUBJECT = 'Thank you for signing up'
GMAIL_EMAIL = ''
GMAIL_PASSWORD = ''


def init():
    logging.info('Beginning Token Collection...')

    return {
        'None': 'None'
    }


def run(stop_flag, shared_memory):
    raffle = NAKED_RAFFLE_NAME
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
                        if NAKED_SUBJECT in email_subject and 'raffle@nakedcph.com' in email_from:
                            print('Naked Email Found for ' + email_to)
                            logging.info('Naked Email Found for ' + email_to)
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
                            i = 0
                            for payload in msg.get_payload():
                                if i == 0:
                                    i += 1
                                    continue
                                # if payload.is_multipart():
                                data = payload.get_payload()
                                #print(data)
                                print('________')

                                # url = data[data.find("(") + 1:data.find(")")]
                                #
                                # url = url.replace('=\n', '').replace('=\r', '')
                                # url = url.replace('\n', '')
                                #
                                # # Find 'h' and 'xid'
                                # params = dict(urllib.parse.parse_qsl(url))
                                #
                                # result = url.replace('https://us5.mailchimp.com/mctx/clicks?url=https%3A%2F%2Fafew-store.us5.list-manage.com%2Fsubscribe%2Fconfirm', '')
                                #
                                # # Find the 'e' param

                                # print(parsed)
                                lower_bound = '"https://app.rule.io/subscriber/'
                                upper_bound = 'CONFI'

                                result = data[data.rindex(lower_bound) : data.rindex(upper_bound)]
                                print(result)

                                result = result.replace('=\n', '').replace('=\r', '')
                                result = result.replace('\n', '')
                                result = result.replace('"https://app.rule.io/subscriber/optIn?token=3D', '')
                                result = result.replace('" style=3D"text-decoration: none;" target=3D"_blank"><span style=3D"color:#FFFFFF;">', '')


                                #
                                # e = result_2.replace(lower_bound, '')
                                #
                                email_info = {
                                    "to": email_to,
                                    "token": result
                                }

                                write_token_to_file(email_info)

        mail.close()
        print('All mail read!')
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
    FILE_PATH = CONFIG.ROOT + '/output/nakednew/Naked_' + NAKED_RAFFLE_NAME + '_tokens.txt'

    if not os.path.exists(FILE_PATH):
        file = open(FILE_PATH, 'w+')
        file.close()

    with open(FILE_PATH, 'a+') as file:
        portalocker.lock(file, portalocker.LOCK_EX)
        file.write(
            data['to'] + ":" +
            data['token'] + "\n"
        )
