import argparse
import asyncio
import json
import sys

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from twikit import Client, Forbidden, TooManyRequests

from cookies import dict_from_cookies_txt
from friends import get_friends, user_to_dict


@retry(retry=(retry_if_exception_type(TooManyRequests) |
              retry_if_exception_type(Forbidden)),
       stop=stop_after_attempt(6),
       wait=wait_fixed(60 * 15))
async def follow_users(client, users, friends):
    while len(users) > 0:
        await asyncio.sleep(60)
        user = users[-1]
        try:
            await client.follow_user(user['id'])
        except Forbidden as e:
            response = json.loads(e.args[0].split(':', 2)[2][2:-1])['errors'][0]
            print(f"[follow_users]:  {user['screen_name']} ({user['id']}) code: {response['code']}, {response["message"]}")
            if (    "You've already requested to follow" in response["message"] or
                    "Cannot find specified user."        in response["message"]):
                friends.append(users.pop())
                continue
            raise
        except Exception as e:
            print(f"[follow_users]: An error occurred:\n{e}")
            raise e

        print(f'[follow_users]: followed {user["screen_name"]}')
        friends.append(users.pop())


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json', type=str)
    parser.add_argument('--cookies', required=True, type=str)
    parser.add_argument('--friends', required=True, type=str)
    args = parser.parse_args()

    with open(args.json) as f:
        users = json.load(f)

    client = Client('en-US', cookies=dict_from_cookies_txt(args.cookies))

    if args.friends:
        with open(args.friends, 'r') as f:
            friends = json.load(f)
    else:
        friends = [user_to_dict(friend) async for friend in get_friends(client, await client.user())]
    friend_ids = [friend['id'] for friend in friends]

    users_to_follow = [user for user in users if user['id'] not in friend_ids]
    try:
        await follow_users(client, users_to_follow, friends)
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        with open(args.friends, 'w') as f:
            json.dump(friends, f)


if __name__ == '__main__':
    asyncio.run(main())
