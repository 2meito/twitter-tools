import logging
import json
from typing import List

from twitter.scraper import Scraper

def get(scraper: Scraper, user_ids: List[int]):
    users = []

    for response in scraper.following(user_ids):
        for instruction in response['data']['user']['result']['timeline']['timeline']['instructions']:
            if instruction['type'] != 'TimelineAddEntries':
                continue
            for entry in instruction['entries']:
                content = entry['content']
                if content['entryType'] != 'TimelineTimelineItem':
                    continue
                itemContent = content['itemContent']
                if itemContent['__typename'] != 'TimelineUser':
                    continue

                user_results = itemContent['user_results']
                if not user_results:
                    continue

                result = user_results['result']

                legacy = result['legacy']

                rest_id = result['rest_id']
                screen_name = legacy['screen_name']
                name = legacy['name']

                users.append({'id': rest_id, 'screen_name': screen_name, 'name': name})

    return users

def parse_json(file_path):
    with open(file_path) as fp:
        users = json.load(fp)
    for user in users:
        print(f'https://twitter.com/{user['screen_name']}', end=' ')
