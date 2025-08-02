import sys
from http import cookiejar
from requests.utils import dict_from_cookiejar

def dict_from_cookies_txt(cookies_txt):
    cj = cookiejar.MozillaCookieJar(cookies_txt)
    cj.load()
    return dict_from_cookiejar(cj)

if __name__ == '__main__':
    print(dict_from_cookies_txt(sys.argv[1]))
