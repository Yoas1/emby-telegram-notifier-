import requests


def convert_list(string):
    li = list(string.split(" "))
    return li


def parser_send(response, t_id, t_token):
    response = response
    t_id = t_id
    t_token = t_token
    text = response['Title']
    data = {"chat_id": t_id, "caption": text, "parse_mode": "Markdown"}
    url_send_photo = f"https://api.telegram.org/bot{t_token}/sendPhoto"
    url_send_message = f"https://api.telegram.org/bot{t_token}/sendMessage"

    if text.startswith("New") & text.endswith('on emby-server'):
        desc = response['Description']
        item = response['Item']
        photo_id = item['Id']
        base_photo_url = (f"http://192.168.1.133:8097/Items/{photo_id}/Images/Primary" if photo_id else None)
        image_response = requests.get(base_photo_url)
        image = ("photo.jpg", image_response.content, "image/jpeg")
        data = {"chat_id": t_id, "caption": text + '\n\nDescription: ' + desc, "parse_mode": "Markdown"}
        response = requests.post(url_send_photo, data=data, files={"photo": image})
    elif text.endswith('removed from emby-server'):
        data["text"] = '🗑 ' + text
        requests.post(url_send_message, data=data)
    elif 'is playing' in text:
        data["text"] = '▶ ' + text
        requests.post(url_send_message, data=data)
    elif 'has finished playing' in text:
        data["text"] = '⏹ ' + text
        requests.post(url_send_message, data=data)
    elif 'has paused' in text:
        data["text"] = '⏸ ' + text
        requests.post(url_send_message, data=data)
    elif 'has resumed' in text:
        data["text"] = '⏯ ' + text
        requests.post(url_send_message, data=data)
    elif text.endswith('is Available for emby-server'):
        item = response['Server']
        server_version = item['Version']
        item = response['PackageVersionInfo']
        new_version = item['versionStr']
        info = item['infoUrl']
        desc = item['description']
        text = f'💾 Update from version {server_version} to {new_version} available \nDescription: {desc} \nMore info: {info}'
        url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={text}"
        requests.post(url)
    elif text.startswith('Failed Login'):
        data["text"] = '🔒 ' + text
        requests.post(url_send_message, data=data)
    elif 'Has Authenticated' in text:
        data["text"] = '🔐 ' + text
        requests.post(url_send_message, data=data)
    elif 'item.markplayed' in text:
        response = response['Item']
        if response['Type'] == 'Movie':
            movie_name = response['Name']
            text = f'✅ Marked-played: {movie_name}'
        elif response['Type'] == 'Episode':
            series_name = response['SeriesName']
            season = response['SeasonName']
            episode_name = response['Name']
            episode_nun = response['IndexNumber']
            text = f'✅ Marked-played: {series_name} {season} episode {episode_nun} - {episode_name}'
        url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={text}"
        requests.post(url)
    elif 'item.markunplayed' in text:
        response = response['Item']
        if response['Type'] == 'Movie':
            movie_name = response['Name']
            text = f'❎ Marked-unplayed: {movie_name}'
        elif response['Type'] == 'Episode':
            series_name = response['SeriesName']
            season = response['SeasonName']
            episode_name = response['Name']
            episode_nun = response['IndexNumber']
            text = f'❎ Marked-unplayed: {series_name} {season} episode {episode_nun} - {episode_name}'
        url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={t_id}&text={text}"
        requests.post(url)
    elif text.startswith('Please Restart'):
        data["text"] = '🔄 ' + text
        requests.post(url_send_message, data=data)
    elif 'Has Been Uninstalled' in text:
        data["text"] = '📤 ' + text
        requests.post(url_send_message, data=data)
    elif 'Installed' in text:
        data["text"] = '📥 ' + text
        requests.post(url_send_message, data=data)
    else:
        data["text"] = text
        requests.post(url_send_message, data=data)
    return text
