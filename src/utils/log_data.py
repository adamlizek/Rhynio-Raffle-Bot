from pymongo import MongoClient
import config as CONFIG

# Storing URI in the code is bad practice but this is old code ok
URI = ""
CLIENT = MongoClient(URI)
DB = CLIENT['RhynioEntries']
ENTRY_DATA = DB.Raffle_Entries
NAKED_ADDRESS_DATA = DB.Naked_Addresses


def log_entry_data(site, raffle, email, proxy, delay='', country=''):
    user = CONFIG.license_key

    ENTRY_DATA.insert_one({
        'user': user,
        'site': site,
        'raffle': raffle,
        'email': email,
        'proxy': proxy,
        'delay': delay,
        'country': country
    })


def check_for_naked_address(email):
    document = NAKED_ADDRESS_DATA.find_one({"email": email})

    if document is None:
        return False
    else:
        return document


def log_naked_address(email, address, instagram):
    exists = check_for_naked_address(email)

    if exists:
        print('Address Exists! Updating')
        update_naked_address(email, address, instagram)
    else:
        print('Address NOT FOUND! Adding')

        obj = {
            'email': email,
            'instagram': instagram,
            'phone_number': address['phone_number'],
            'address_1': address['address_1'],
            'zip': address['zip'],
            'city': address['city'],
            'country': address['country']
        }

        NAKED_ADDRESS_DATA.insert_one(obj)


def update_naked_address(email, address, instagram):
    obj = {
        'instagram': instagram,
        'phone_number': address['phone_number'],
        'address_1': address['address_1'],
        'zip': address['zip'],
        'city': address['city'],
        'country': address['country']
    }

    query = {"email": email}
    new_values = {"$set": obj}
    NAKED_ADDRESS_DATA.update_one(query, new_values)
