def get(file_path):
    cookies = {'auth_token': None, 'ct0': None}
    with open(file_path) as file:
        for line in file:
            if line.isspace():
                continue
            if line.startswith('#'):
                continue
            cookie = line.split()
            if cookie[0] not in ['.x.com', '.twitter.com']:
                continue
            if cookie[5] == 'auth_token':
                cookies['auth_token'] = cookie[6]
            if cookie[5] == 'ct0':
                cookies['ct0'] = cookie[6]
    return cookies