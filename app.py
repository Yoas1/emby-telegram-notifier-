from flask import Flask, request, abort
import requests
from os import environ

app = Flask(__name__)
t_id = environ['TID']
t_token = environ['TT']
e_server = environ['E_SERVER']
url_send_photo = f"https://api.telegram.org/bot{t_token}/sendPhoto"
url_send_message = f"https://api.telegram.org/bot{t_token}/sendMessage"


def convert_list(string):
    li = list(string.split(" "))
    return li


def get_icon(argument):
    switcher = {
        'playback.start': '▶ ',
        'playback.stop': '⏹ ',
        'playback.pause': '⏸ ',
        'playback.unpause': '⏯ ',
        'library.deleted': '🗑 ',
        'item.markunplayed': '❎',
        'item.markplayed': '✅',
        'system.updateavailable': '💾',
        'user.authenticationfailed': '🔒',
        'user.authenticated': '🔐',
        'system.serverrestartrequired': '🔄',
        'plugins.pluginuninstalled': '📤',
        'plugins.plugininstalled': '📥',
    }
    return switcher.get(argument, '')


def update():
    global response
    item = response['Server']
    server_version = item['Version']
    item = response['PackageVersionInfo']
    new_version = item['versionStr']
    info = item['infoUrl']
    desc = item['description']
    get_event_marked = response['Event']
    icon = get_icon(get_event_marked)
    text = f'{icon} Update from version {server_version} to {new_version} available \nDescription: {desc} \nMore info: {info}'
    url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
    requests.post(url)


def marked():
    global response, text
    get_event_marked = response['Event']
    response = response['Item']
    icon = get_icon(get_event_marked)
    if 'item.markplayed' in get_event_marked:
        if response['Type'] == 'Movie':
            movie_name = response['Name']
            text = f'{icon} Marked-played: {movie_name}'
        elif response['Type'] == 'Episode':
            series_name = response['SeriesName']
            season = response['SeasonName']
            episode_name = response['Name']
            episode_nun = response['IndexNumber']
            text = f'{icon} Marked-played: {series_name} {season} episode {episode_nun} - {episode_name}'
        url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
        requests.post(url)
    elif 'item.markunplayed' in get_event_marked:
        if response['Type'] == 'Movie':
            movie_name = response['Name']
            text = f'{icon} Marked-unplayed: {movie_name}'
        elif response['Type'] == 'Episode':
            series_name = response['SeriesName']
            season = response['SeasonName']
            episode_name = response['Name']
            episode_nun = response['IndexNumber']
            text = f'{icon} Marked-unplayed: {series_name} {season} episode {episode_nun} - {episode_name}'
        url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
        requests.post(url)


def send_message():
    get_event = response['Event']
    text_new = response['Title']
    icon = get_icon(get_event)
    data = {"chat_id": send_id, "caption": text_new, "parse_mode": "Markdown", "text": icon + text_new}
    requests.post(url_send_message, data=data)


def lib_new():
    text_new = response['Title']
    desc = response['Description']
    item = response['Item']
    photo_id = item['Id']
    base_photo_url = (f"{e_server}/emby/Items/{photo_id}/Images/Primary" if photo_id else None)
    image_response = requests.get(base_photo_url)
    image = ("photo.jpg", image_response.content, "image/jpeg")
    data_new = {"chat_id": send_id, "caption": text_new + '\n\nDescription: ' + desc, "parse_mode": "Markdown"}
    requests.post(url_send_photo, data=data_new, files={"photo": image})


def switch_case(argument):
    switcher = {
        'playback.start': send_message,
        'playback.stop': send_message,
        'playback.pause': send_message,
        'playback.unpause': send_message,
        'library.new': lib_new,
        'library.deleted': send_message,
        'item.markunplayed': marked,
        'item.markplayed': marked,
        'system.updateavailable': update,
        'user.authenticationfailed': send_message,
        'user.authenticated': send_message,
        'system.serverrestartrequired': send_message,
        'plugins.pluginuninstalled': send_message,
        'plugins.plugininstalled': send_message,
    }
    return switcher.get(argument, '')


@app.route('/webhook', methods=['POST'])
def webhook():
    global list_id, response, send_id
    if request.method == 'POST':
        response = request.json
        list_id = convert_list(t_id)
        for i in range(len(list_id)):
            send_id = list_id[i]
            get_event_now = response['Event']
            print(get_event_now)
            arg_check = ('playback.start',
                         'playback.stop',
                         'playback.pause',
                         'playback.unpause',
                         'library.new',
                         'library.deleted',
                         'item.markunplayed',
                         'item.markplayed',
                         'system.updateavailable',
                         'user.authenticationfailed',
                         'user.authenticated',
                         'system.serverrestartrequired',
                         'plugins.pluginuninstalled',
                         'plugins.plugininstalled'
            )
            if get_event_now.startswith(arg_check):
                switch_case(get_event_now)()
            else:
                send_message()
        return 'success', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run()