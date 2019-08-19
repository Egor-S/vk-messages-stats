import re
import webbrowser

# format: client_id, scope, version
AUTH_PATTERN = "https://oauth.vk.com/authorize?client_id={}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope={}&response_type=token&v={}"
SCOPE_BITS = {
    "notify": 1,
    "friends": 2,
    "photos": 4,
    "audio": 8,
    "video": 16,
    "stories": 64,
    "pages": 128,
    "256": 256,
    "status": 1024,
    "notes": 2048,
    "messages": 4096,
    "wall": 8192,
    "ads": 32768,
    "offline": 65536,
    "docs": 131072,
    "groups": 262144,
    "notifications": 524288,
    "stats": 1048576,
    "email": 4194304,
    "market": 134217728
}


class UnknownScope(BaseException):
    def __init__(self, scope):
        self.scope = scope

    def __repr__(self):
        return "Unknown scope: {}".format(self.scope)


class IncorrectRedirectedURL(BaseException):
    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "Incorrect redirected URL: {}".format(self.url)


def scope_to_bitmask(scope):
    bitmask = 0
    for s in scope:
        if s not in SCOPE_BITS:
            raise UnknownScope(s)
        bitmask += SCOPE_BITS[s]
    return bitmask


def parse_redirected_url(url):
    res = re.search(r"access_token=([\da-f]+)", url)
    if res:
        token = res.group(1)
    else:
        raise IncorrectRedirectedURL(url)
    res = re.search(r"expires_in=([\d]+)", url)
    if res:
        expires_in = res.group(1)
    else:
        raise IncorrectRedirectedURL(url)
    res = re.search(r"user_id=([\d]+)", url)
    if res:
        user_id = res.group(1)
    else:
        raise IncorrectRedirectedURL(url)
    return token, int(expires_in), int(user_id)


def get_token_by_implicit_flow(client_id, scope, v='5.92', verbose=True):
    bitmask = scope_to_bitmask(scope)
    auth_link = AUTH_PATTERN.format(client_id, bitmask, v)
    print("Authorization link:", auth_link)
    webbrowser.open_new_tab(auth_link)

    redirected_url = input("Redirected URL: ")
    token, expires_in, user_id = parse_redirected_url(redirected_url)
    if verbose:
        print("Token:", token)
        print("Expires in: {:02d}:{:02d}:{:02d}".format(expires_in // 3600, (expires_in // 60) % 60, expires_in % 60))
        print("User id:", user_id)

    return token, expires_in, user_id
