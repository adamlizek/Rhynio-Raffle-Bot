import random
from random import randint
import string
import os
import config as CONFIG


def get_random_password():
    return get_random_string(8) + str(random.randint(10, 99))


def get_random_string(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


def convert_state(state):
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Palau': 'PW',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
    }

    abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

    if len(state) == 2:
        try:
            result = abbrev_us_state[state]
        except KeyError:
            result = None
    else:
        try:
            result = us_state_abbrev[state]
        except KeyError:
            result = None

    return result


def generate_emails(catchall, amount):
    with open(CONFIG.ROOT + '/data/info/first_names.txt', 'r') as file:
        first_names = list(file.read().split())

    with open(CONFIG.ROOT + '/data/info/last_names.txt', 'r') as file:
        last_names = list(file.read().split())

    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/generated_emails.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        for x in range(amount):
            first = random.choice(first_names)
            last = random.choice(last_names)

            file.write(first + last + str(randint(100, 999)) + '@' + catchall + '\n')

    print('Done!')
