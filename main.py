import json
import os
from pathlib import Path

import requests
from checkip.ip import resolve_ip


# Config
CONFIG_PATH = os.environ.get('DF_CONFIG_PATH', Path.joinpath(Path(__file__).resolve().parent, 'config.json'))

Path.joinpath(Path(__file__).resolve().parent, 'config.json')

with open(CONFIG_PATH) as jsonFile:
    config_json = json.load(jsonFile)

CLOUDFLARE_TOKEN = config_json['cloudflare_token']


# Helpers
def get_zone_id(domain_name):
    response = requests.get(
        url='https://api.cloudflare.com/client/v4/zones',
        headers={
            'Authorization': 'Bearer {}'.format(CLOUDFLARE_TOKEN)
        },
        params={
            'name': domain_name
        }
    )

    response.raise_for_status()

    return response.json()['result'][0]['id']

def get_record_data(zone_id, record_name):
    response = requests.get(
        url='https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(zone_id),
        headers={
            'Authorization': 'Bearer {}'.format(CLOUDFLARE_TOKEN)
        },
        params={
            'type': 'A',
            'name': record_name
        }
    )

    response.raise_for_status()

    result = response.json()['result']

    return result[0]['id'], result[0]['content']

def update_record_ip(zone_id, record_id, ip):
    response = requests.patch(
        url='https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(zone_id, record_id),
        headers={
            'Authorization': 'Bearer {}'.format(CLOUDFLARE_TOKEN)
        },
        json={
            'content': ip
        }
    )

    response.raise_for_status()


# Main
ip = resolve_ip(['cloudflare', 'dyndns', 'freedns', 'googledomains'])

for record in config_json['records']:
    zone_id = get_zone_id(record['domain'])
    record_id, record_ip = get_record_data(zone_id, record['record'])

    if record_ip == ip:
        continue

    update_record_ip(zone_id, record_id, ip)
