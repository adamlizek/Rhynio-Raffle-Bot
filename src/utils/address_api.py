from requests import get
import config


def get_address(country='United States'):
    # Get Address of matching country from our API
    if country == 'United States' or country == 'US':
        try:
            address = get(config.address_api_endpoint + '/api/address?country=US', timeout=15).json()
            return address[0]
        except Exception as e:
            print('Error' + str(e))
            return False
