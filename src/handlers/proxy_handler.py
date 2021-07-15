import config as CONFIG
import json


def parse_into_request_format(unformatted_proxies):
    formatted_proxies = []

    for proxy in unformatted_proxies:
        if len([x.strip() for x in proxy.split(':')]) == 4:
            IP, PORT, USER, PASS = [x.strip() for x in proxy.split(':')]

            formatted_proxies.append({
                'http': f'http://{USER}:{PASS}@{IP}:{PORT}',
                'https': f'https://{USER}:{PASS}@{IP}:{PORT}'
            })
        else:
            IP, PORT = [x.strip() for x in proxy.split(':')]

            formatted_proxies.append({
                'http': f'http://{IP}:{PORT}',
                'https': f'https://{IP}:{PORT}'
            })

    return formatted_proxies


def parse_into_default_form(unformatted_proxy):
    proxy = unformatted_proxy['http'][7:]
    proxy = proxy.replace("@", ":")

    result_from_parsing = [x.strip() for x in proxy.split(':')]
    if len(result_from_parsing) == 4:
        proxy_parsed = result_from_parsing[2] + ":" + result_from_parsing[3] + ":" + \
                       result_from_parsing[0] + ":" + result_from_parsing[1]
    else:
        proxy_parsed = result_from_parsing[0] + ":" + result_from_parsing[1]

    return proxy_parsed


def parse_single_proxy_to_request(unformatted_proxy):
    if len([x.strip() for x in unformatted_proxy.split(':')]) == 4:
        IP, PORT, USER, PASS = [x.strip() for x in unformatted_proxy.split(':')]

        formatted_proxy = {
            'http': f'http://{USER}:{PASS}@{IP}:{PORT}',
            'https': f'https://{USER}:{PASS}@{IP}:{PORT}'
        }
    else:
        IP, PORT = [x.strip() for x in unformatted_proxy.split(':')]

        formatted_proxy = {
            'http': f'http://{IP}:{PORT}',
            'https': f'https://{IP}:{PORT}'
        }

    return formatted_proxy


def get_proxy_list():
    with open(CONFIG.ROOT + '/data/proxies/proxy_lists.json', 'r') as json_file:
        data = json.load(json_file)

        list_id = 0
        while list_id < len(data['proxies']):
            if data['proxies'][list_id]['list_name'] == CONFIG.PROXY_LIST_NAME:
                break

        unformatted_proxy_list = data['proxies'][list_id]['proxies']
        proxies = parse_into_request_format(unformatted_proxy_list)

    return proxies
