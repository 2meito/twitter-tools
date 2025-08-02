import argparse
import asyncio
import json
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from twikit import Client, Forbidden, TooManyRequests

from cookies import dict_from_cookies_txt
from friends import get_friends


@retry(retry=(retry_if_exception_type(TooManyRequests) |
              retry_if_exception_type(Forbidden)),
       stop=stop_after_attempt(6),
       wait=wait_fixed(60 * 15))
async def follow_users(client, users):
    await asyncio.sleep(60)
    while len(users) > 0:
        user = users[-1]
        try:
            await client.follow_user(user['id'])
        except Forbidden as e:
            if "You've already requested to follow" in e.args[0]:
                print(f"[follow_users]: already followed {user['screen_name']}")
                users.pop()
                continue
            raise e
        except Exception as e:
            print(f"[follow_users]: An error occurred:\n{e}")
            raise e

        print(f'[follow_users]: followed {user["screen_name"]}')
        users.pop()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json', type=str)
    parser.add_argument('--cookies', required=True, type=str)
    args = parser.parse_args()

    with open(args.json) as f:
        users = json.load(f)

    client = Client('en-US', cookies=dict_from_cookies_txt(args.cookies))

    friends = [friend async for friend in get_friends(client, await client.user())]
    friend_ids = [friend.id for friend in friends]
    users_to_follow  = [user for user in users if user['id'] not in friend_ids]
    await follow_users(client, users_to_follow)


if __name__ == '__main__':
    asyncio.run(main())
