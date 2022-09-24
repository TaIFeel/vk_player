import requests

token = None

def auth(login:str, password:str, two_fa:bool = False, code:str=None, captcha_key:str=None, captcha_sid:str=None):
    global token
    response = requests.get(f'https://oauth.vk.com/token', params={
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

    print(response)

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

"""response = auth(login, password)

#if 'need_captcha' in response:
    captcha_keys = input(f"Введите капчу ({response['captcha_img']}: ")
    response = auth(login, password, captcha_key=captcha_keys, captcha_sid=response['captcha_sid'])

#if 'validation_sid' in response:
    print(response)
    b = session.get("https://api.vk.com/method/auth.validatePhone", params={'sid': response['validation_sid'],'v': '5.131'}).json()
    bc = session.get(response['redirect_uri'])
    print(bc)
    response = auth(login, password)
    print(b)
    code = input('Введите код из смс:  ')
    response = auth(login, password, two_fa=True, code=code)   

if 'access_token' in response:
    token = response['access_token']
    try:
        requests.get('https://api.vk.com/method/messages.send?v=5.130', params={
            'access_token': token,
            'message': f'Ваш токен: {token}',
            'peer_id': response['user_id'],
            'random_id': 0
        })
        print('Токен отправлен в избранное.')
    except:
        print('Не удалось отправить токен в избранное.')
    print(f'Ваш токен: {token}')
else:
    print(response)"""


# Thanks,
# Vk: https://vk.com/id266287518, https://vk.com/id230192963.

# Written with love. By Alexey Kuznetsov.
# Bug reports write here -> https://vk.me/id194861150

