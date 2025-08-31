import argparse
import asyncio
import datetime
import json
from pathlib import Path
from twikit import Client, Forbidden, TooManyRequests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from cookies import dict_from_cookies_txt


def user_to_dict(user):
    return {'id': user.id, 'screen_name': user.screen_name, 'name': user.name}

@retry(retry=(retry_if_exception_type(TooManyRequests) |
              retry_if_exception_type(Forbidden)),
       stop=stop_after_attempt(6),
       wait=wait_fixed(60 * 15))
async def get_friends(client, user, friends=None, count=0):
    await asyncio.sleep(90)
    try:
        if count == 0:
            friends = await client.get_user_following(user.id, count=50)
        if not friends:
            return
        for friend in friends:
            yield friend
        count += len(friends)
        print(f'[get_friends]: got {count} friends in total...')
        async for friend in get_friends(None, None, await friends.next(), count):
            yield friend
    except Exception as e:
        print(f'[get_friends]: An error occurred:\n{e}')
        raise e


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('screen_names', nargs='+', type=str)
    parser.add_argument('--cookies', required=True, type=str)
    args = parser.parse_args()

    client = Client('en-US', cookies=dict_from_cookies_txt(args.cookies))

    Path('out').mkdir(parents=True, exist_ok=True)
    users = [await client.get_user_by_screen_name(screen_name) for screen_name in args.screen_names]
    for user in users:
        friend_list = []
        base_path = f'out/{user.screen_name}-{datetime.datetime.now().strftime("%Y%m%d.%H%M%S-%f")}'
        with open(f'{base_path}.txt', 'w') as file:
            async for friend in get_friends(client, user):
                friend_list.append(user_to_dict(friend))
                file.write(f'https://twitter.com/{friend.screen_name}\n')
        with open(f'{base_path}.json', 'w') as file:
            file.write(json.dumps(friend_list))


if __name__ == '__main__':
    asyncio.run(main())
