import requests

token = None

def auth(login:str, password:str, two_fa:bool = False, code:str=None, captcha_key:str=None, captcha_sid:str=None):
    global token
    response = requests.post(f'https://oauth.vk.com/token', params={
        'grant_type': 'password',
        'client_id': '6146827',
        'client_secret': 'qVxWRF1CwHERuIrKBnqe',
        'username': login,
        'password': password,
        'v': '5.89',
        '2fa_supported': '1',
        'force_sms': '1',
        'code': code if two_fa else None
    }).json()

    token = response['access_token']

    return requests.get(
        "https://api.vk.com/method/audio.get",
        params=[('access_token', response['access_token']),
                ("count", 100),
                ("offset", 0),
                ('v', '5.89')]
    ).json()

    


def get_music_token(token):
    return requests.get(
        "https://api.vk.com/method/audio.get",
        params=[('access_token', token),
                ("count", 100),
                ("offset", 0),
                ('v', '5.89')]
    ).json()
