from faker import Faker
import config as CONFIG
import random
from random import randint


# Ugly Faker Code Below
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def validAddress(inputString):
    return 'PSC' in inputString or 'Unit' in inputString


def generate_naked_address(country):
    if country == 'United States':
        fake = Faker('en_US')

        area_codes = None
        with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
            area_codes = list(file.read().splitlines())

        area_code = random.choice(area_codes)

        phone_number = '+1' + area_code + str(randint(1111111, 9999999))

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.zipcode(),
            'state': fake.state(),
            'phone_number': phone_number,
            'country': 'US',
        }

        if hasNumbers(address['address_1']) and not validAddress(address['address_1']):
            return address
        else:
            return generate_naked_address('United States')

    elif country == 'Germany':
        fake = Faker('de_DE')

        phone_number = fake.phone_number()
        if phone_number[:3] != '+49':
            phone_number = '+49' + phone_number

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': phone_number,
            'country': 'DE',
        }

        return address

    elif country == 'France':
        fake = Faker('fr_FR')

        phone_number = fake.phone_number()

        if phone_number[:3] != '+33':
            phone_number = '+33' + phone_number

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': fake.phone_number(),
            'country': 'FR',
        }

        return address

    elif country == 'Portugal':
        fake = Faker('pt_PT')

        phone_number = fake.phone_number()

        if phone_number[:4] != '+351':
            if phone_number[:5] == '(351)':
                phone_number = phone_number.replace('(351)', '+351')
            else:
                phone_number = '+351' + phone_number

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': phone_number,
            'country': 'PT',
        }

        return address

    elif country == 'Spain':
        fake = Faker('es_ES')

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': fake.phone_number(),
            'country': 'DK',
        }

        return address

    elif country == 'United Kingdom':
        fake = Faker('en_GB')
        phone_number = fake.phone_number()

        if phone_number[:3] != '+44':
            phone_number = '+44' + phone_number

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': phone_number,
            'country': 'GB',
        }

        return address

    elif country == 'Romania':
        fake = Faker('ro_RO')

        phone_number = '+4021' + str(randint(0000000, 9999999))

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': phone_number,
            'country': 'RO',
        }

        return address

    elif country == 'Denmark':
        fake = Faker('dk_DK')
        phone_number = '+45' + str(randint(11111111,99999999))

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.zipcode(),
            'phone_number': phone_number,
            'country': 'DK',
        }

        return address

    elif country == 'Sweden':
        fake = Faker('sv_SE')
        phone_number = '+46' + str(randint(11111111,99999999))

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': phone_number,
            'country': 'SE',
        }

        return address

    elif country == 'Norway':
        fake = Faker('no_NO')
        phone_number = '+47' + str(randint(11111111,99999999))

        address = {
            'address_1': fake.building_number() + ' ' + fake.street_name(),
            'city': fake.city(),
            'zip': fake.postcode(),
            'phone_number': phone_number,
            'country': 'NO',
        }

        return address


def generate_yme_phone_number(country):
    if country == 'United States':
        with open(CONFIG.ROOT + '/data/info/area_codes.txt', 'r') as file:
            area_codes = list(file.read().splitlines())

        area_code = random.choice(area_codes)

        #phone_number = '+1' + area_code + str(randint(1111111, 9999999))
        phone_number = area_code + str(randint(1111111, 9999999))

        return phone_number

    elif country == 'Germany':
        fake = Faker('de_DE')

        phone_number = fake.phone_number()
        if phone_number[:3] != '+49':
            phone_number = '+49' + phone_number

        return phone_number

    elif country == 'France':
        fake = Faker('fr_FR')

        phone_number = fake.phone_number()

        if phone_number[:3] != '+33':
            phone_number = '+33' + phone_number

        return phone_number

    elif country == 'Portugal':
        fake = Faker('pt_PT')

        phone_number = fake.phone_number()

        if phone_number[:4] != '+351':
            if phone_number[:5] == '(351)':
                phone_number = phone_number.replace('(351)', '+351')
            else:
                phone_number = '+351' + phone_number

        return phone_number

    elif country == 'Spain':
        fake = Faker('es_ES')
        phone_number = fake.phone_number()

        return phone_number

    elif country == 'United Kingdom':
        fake = Faker('en_GB')
        phone_number = fake.phone_number()

        if phone_number[:3] != '+44':
            phone_number = '+44' + phone_number

        return phone_number

    elif country == 'Romania':
        phone_number = '+4021' + str(randint(0000000, 9999999))

        return phone_number

    elif country == 'Denmark':
        phone_number = '+45' + str(randint(11111111, 99999999))

        return phone_number

    elif country == 'Norway':
        phone_number = '+47' + str(randint(11111111, 99999999))

        return phone_number


def generate_country_faker(country):
    if country == 'United States':
        fake = Faker('en_US')
        return fake

    elif country == 'Germany':
        fake = Faker('de_DE')

        return fake

    elif country == 'France':
        fake = Faker('fr_FR')

        return fake

    elif country == 'Portugal':
        fake = Faker('pt_PT')

        return fake

    elif country == 'Spain':
        fake = Faker('es_ES')

        return fake

    elif country == 'United Kingdom':
        fake = Faker('en_GB')

        return fake

    elif country == 'Romania':
        fake = Faker('ro_RO')

        return fake

    elif country == 'Denmark':
        fake = Faker('dk_DK')

        return fake

    elif country == 'Canada':
        fake = Faker('en_CA')

        return fake


def random_state():
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "District of Columbia",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Louisiana",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virgina",
        "Wisconsin",
        "Wyoming"
    ]

    return random.choice(states)
