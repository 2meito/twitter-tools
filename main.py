import argparse
import datetime
import json
import re
import time
import os
from pathlib import Path
from twitter.scraper import Scraper

import cookies
import follows

path = Path(f'logs{os.path.sep}{time.strftime('%Y%m%d%H%M%S')}.log')
path.parent.mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('screen_names', nargs='+', type=str)
    parser.add_argument('--cookies', required=True, type=str)
    args = parser.parse_args()

    with open(args.cookies) as file:
        scraper = Scraper(cookies=cookies.get(args.cookies))

    screen_names = []
    for screen_name in args.screen_names:
        m = re.match(r'(?:https?://(?:x|twitter).com/)?@?(\w{1,15})', screen_name)
        screen_names.append(m.group(1))

    accounts = list(map(lambda x: {
        'screen_name': x['data']['user']['result']['legacy']['screen_name'],
        'id': int(x['data']['user']['result']['rest_id'])
    }, scraper.users(screen_names)))

    for account in accounts:
        base_path = f'out/{account['screen_name']}-{datetime.datetime.now().strftime("%Y%m%d.%H%M%S-%f")}'
        users = follows.get(scraper, [account['id']])
        with open(f'{base_path}.json', 'w') as file:
            file.write(json.dumps(users))
        with open(f'{base_path}.txt', 'w') as file:
            for user in users:
                file.write(f'https://twitter.com/{user['screen_name']}\n')