import json
import logging
import os
from pathlib import Path

import requests
from checkip import resolve_ip


### Config

CONFIG_PATH = os.environ.get('DF_CONFIG_PATH', Path.joinpath(Path(__file__).resolve().parent, 'config.json'))

Path.joinpath(Path(__file__).resolve().parent, 'config.json')

with open(CONFIG_PATH) as f:
    config_json = json.load(f)

CLOUDFLARE_TOKEN = config_json['cloudflare_token']

DISCORD_WEBHOOK_URLS = config_json.get('discord_webhook_urls', [])


### Logging

logger = logging.getLogger('dynamicflare')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)


### Helpers

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


def report_to_dicord(domain, record, ip):
    message = '`({}, {}) - IP updated: {}`'.format(domain, record, ip)
    for discord_webhook_url in DISCORD_WEBHOOK_URLS:
        requests.post(
            url=discord_webhook_url,
            data={
                'content': message
            }
        )

### Main

# Resolve IP
logger.info('Resolving IP.')
ip = resolve_ip(['cloudflare', 'dyndns', 'freedns', 'googledomains'])
logger.info('Resolved IP: {}.'.format(ip))

# Update records
for record in config_json['records']:
    logger.info('{} - Updating.'.format((record['domain'], record['record'])))

    # Get zone ID
    logger.info('{} - Getting zone ID.'.format((record['domain'], record['record'])))
    zone_id = get_zone_id(record['domain'])
    logger.info('{} - Got zone ID: {}.'.format((record['domain'], record['record']), zone_id))
    logger.info('{} - Getting record ID and record IP.'.format((record['domain'], record['record'])))

    # Get record ID and record IP
    record_id, record_ip = get_record_data(zone_id, record['record'])
    logger.info('{} - Got record ID and record IP: {}, {}.'.format((record['domain'], record['record']), record_id, record_ip))

    if record_ip == ip:
        logger.info('{} - Same resolved IP and record IP. Skipping update.'.format((record['domain'], record['record'])))
        continue

    # Update record IP
    logger.info('{} - Updating record IP.'.format((record['domain'], record['record'])))
    update_record_ip(zone_id, record_id, ip)
    logger.info('{} - Record IP updated: {}.'.format((record['domain'], record['record']), ip))

    # Report to discord
    if DISCORD_WEBHOOK_URLS:
        logger.info('{} - Reporting to discord.'.format((record['domain'], record['record'])))
        report_to_dicord(record['domain'], record['record'], ip)
        logger.info('{} - Reported to discord: {}.'.format((record['domain'], record['record']), ip))
