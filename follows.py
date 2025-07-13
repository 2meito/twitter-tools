import argparse
import asyncio
import datetime
import json
from pathlib import Path
from twikit import Client


async def get_friends(client, user):
    friends = await client.get_user_following(user.id, count=50)
    count = len(friends)
    while friends:
        for friend in friends:
            yield friend
        friends = await friends.next()
        count += len(friends)
        print(f'processed {count} friends...')


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('screen_names', nargs='+', type=str)
    parser.add_argument('--username', required=False, type=str)
    parser.add_argument('--password', required=False, type=str)
    parser.add_argument('--cookies', required=False, type=str)
    parser.add_argument('--save-cookies', required=False, type=str)
    args = parser.parse_args()

    client = Client('en-US')
    if args.cookies:
        client.load_cookies(args.cookies)
    elif args.username and args.password:
        await client.login(
            auth_info_1=args.username,
            password=args.password,
        )
        if args.save_cookies:
            with open(args.save_cookies, 'w') as file:
                file.write(json.dumps(client.get_cookies()))
    else:
        raise "No credentials or cookies supplied."

    Path('out').mkdir(parents=True, exist_ok=True)
    users = [await client.get_user_by_screen_name(screen_name) for screen_name in args.screen_names]
    for user in users:
        friend_list = []
        base_path = f'out/{user.screen_name}-{datetime.datetime.now().strftime("%Y%m%d.%H%M%S-%f")}'
        with open(f'{base_path}.txt', 'w') as file:
            async for friend in get_friends(client, user):
                friend_list.append({'id': friend.id, 'screen_name': friend.screen_name, 'name': friend.name})
                file.write(f'https://twitter.com/{friend.screen_name}\n')
        with open(f'{base_path}.json', 'w') as file:
            file.write(json.dumps(friend_list))


if __name__ == '__main__':
    asyncio.run(main())
