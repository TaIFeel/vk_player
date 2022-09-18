import requests
from vkaudiotoken import get_kate_token, TokenException, get_vk_official_token
token = None
user_agent = None

def get_music(login, password, code = None):
    global token, user_agent
    sess = requests.session()

    try:
        info = get_vk_official_token(login, password, code)

        sess.headers.update({'User-Agent': info["user_agent"]})

        track_list = sess.get(
            "https://api.vk.com/method/audio.get",
            params=[('access_token', info['token']),
                    ("count", 100),
                    ("offset", 0),
                    ('v', '5.89')]
        ).json()

        token = info['token']
        user_agent = info['user_agent']
        return track_list

            #for i, track in enumerate(track_list['response']['items']):
                #tracks.append({i: {f"title": track['title'], "url": track['url']}})

    except TokenException as exc:
        return exc

def get_music_token(token, user_agent):
    sess = requests.session()

    try:
        sess.headers.update({'User-Agent': user_agent})

        track_list = sess.get(
            "https://api.vk.com/method/audio.get",
            params=[('access_token', token),
                    ("count", 100),
                    ("offset", 0),
                    ('v', '5.89')]
        ).json()


        return track_list

            #for i, track in enumerate(track_list['response']['items']):
                #tracks.append({i: {f"title": track['title'], "url": track['url']}})

    except TokenException as exc:
        return exc

