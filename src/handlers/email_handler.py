import config as CONFIG
import queue
import json
from src.handlers.email import Email


def get_email_queue():
    with open(CONFIG.ROOT + '/data/emails/emails.json', 'r') as json_file:
        data = json.load(json_file)
        email_queue = queue.Queue()
        for e in data['emails']:
            split_string = e.split(':')
            email = split_string[0]

            if len(split_string) == 3:
                temp_email = Email(email, firstname=split_string[1], lastname=split_string[2])
            else:
                temp_email = Email(email)
            email_queue.put(temp_email)

    return email_queue
