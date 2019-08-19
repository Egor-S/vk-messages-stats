import json
import datetime as dt
from utils.implicitflow import get_token_by_implicit_flow

if __name__ == '__main__':
    scopes = ['messages']
    token, expires_in, user_id = get_token_by_implicit_flow(6823485, scopes)
    with open("token.secret", 'w') as fout:
        json.dump({
            'token': token,
            'expires': int(dt.datetime.now().timestamp()) + expires_in,
            'user_id': user_id,
            'scopes': scopes
        }, fout, indent=2)
