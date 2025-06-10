from flask import Flask, request, abort
import requests
from os import environ
import yaml

app = Flask(__name__)


def get_token():
  with open("/config/config.yaml") as data:
    info_data = yaml.safe_load(data)
  token = info_data["token"]
  token = token[0]
  return token


def get_emby_url():
  with open("/config/config.yaml") as data:
    info_data = yaml.safe_load(data)
  server = info_data["emby-server"]
  server = server[0]
  return server


t_token = get_token()
url_send_photo = f"https://api.telegram.org/bot{t_token}/sendPhoto"
url_send_message = f"https://api.telegram.org/bot{t_token}/sendMessage"
e_server = get_emby_url()
item_id = ""



def get_admins():
  with open("/config/config.yaml") as data:
    info_data = yaml.safe_load(data)
  try:
    admins = info_data["admins"]
    return admins
  except KeyError:
    return None


def get_users():
  with open("/config/config.yaml") as data:
    info_data = yaml.safe_load(data)
  try:
    users = info_data["users"]
    return users
  except KeyError:
    return None


def convert_list(string):
  li = list(string.split(" "))
  return li


def get_icon(argument):
  switcher = {
    "playback.start": "▶ ",
    "playback.stop": "⏹ ",
    "playback.pause": "⏸ ",
    "playback.unpause": "⏯ ",
    "library.deleted": "🗑 ",
    "item.markunplayed": "❎",
    "item.markplayed": "✅",
    "system.updateavailable": "💾",
    "user.authenticationfailed": "🔒",
    "user.authenticated": "🔐",
    "system.serverrestartrequired": "🔄",
    "plugins.pluginuninstalled": "📤",
    "plugins.plugininstalled": "📥",
  }
  return switcher.get(argument, "")


def update():
  global response
  item = response["Server"]
  server_version = item["Version"]
  item = response["PackageVersionInfo"]
  new_version = item["versionStr"]
  info = item["infoUrl"]
  desc = item["description"]
  get_event_marked = response["Event"]
  icon = get_icon(get_event_marked)
  text = f"{icon} Update from version {server_version} to {new_version} available \nDescription: {desc} \nMore info: {info}"
  url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
  requests.post(url)


def rate():
    global response
    user = response['User']['Name']
    item = response['Item']['Name']
    add_favorite = response['Item']['UserData']['IsFavorite']
    if add_favorite == True:
        text = user + '\n👍🏻 added: ' + item + ' to favorites'
    elif add_favorite == False:
        text = user + '\n👎🏻 remove: ' + item + ' from favorites'
    url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
    requests.post(url)


def marked():
  global response, text
  get_event_marked = response["Event"]
  response = response["Item"]
  icon = get_icon(get_event_marked)
  if "item.markplayed" in get_event_marked:
    if response["Type"] == "Movie":
      movie_name = response["Name"]
      text = f"{icon} Marked-played: {movie_name}"
    elif response["Type"] == "Episode":
      series_name = response["SeriesName"]
      season = response["SeasonName"]
      episode_name = response["Name"]
      episode_nun = response["IndexNumber"]
      text = f"{icon} Marked-played: {series_name} {season} episode {episode_nun} - {episode_name}"
    url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
    requests.post(url)
  elif "item.markunplayed" in get_event_marked:
    if response["Type"] == "Movie":
      movie_name = response["Name"]
      text = f"{icon} Marked-unplayed: {movie_name}"
    elif response["Type"] == "Episode":
      series_name = response["SeriesName"]
      season = response["SeasonName"]
      episode_name = response["Name"]
      episode_nun = response["IndexNumber"]
      text = f"{icon} Marked-unplayed: {series_name} {season} episode {episode_nun} - {episode_name}"
    url = f"https://api.telegram.org/bot{t_token}/sendMessage?chat_id={send_id}&text={text}"
    requests.post(url)


def send_message():
  get_event = response["Event"]
  text_new = response["Title"]
  icon = get_icon(get_event)
  data = {
    "chat_id": send_id,
    "caption": text_new,
    "parse_mode": "Markdown",
    "text": icon + text_new,
  }
  requests.post(url_send_message, data=data)


def lib_new():
  global item_id
  text_new = response["Title"]
  try:
    desc = response["Description"]
  except KeyError:
    desc = (
      "**Can't get a description from the server, edit its identity manually**"
    )
  item = response["Item"]
  photo_id = item["Id"]
  try:
    rating = item['CommunityRating']
  except:
    pass
  base_photo_url = (
    f"{e_server}/emby/Items/{photo_id}/Images/Primary" if photo_id else None
  )
  image_response = requests.get(base_photo_url)
  image = ("photo.jpg", image_response.content, "image/jpeg")
  try:
    data_new = {"chat_id": send_id, "caption": text_new + '\n' + 'Rating: ' + str(rating) + '🌟' + '\n\nDescription: ' + desc, "parse_mode": "Markdown"}
  except:
    data_new = {"chat_id": send_id, "caption": text_new + '\n\nDescription: ' + desc, "parse_mode": "Markdown"}
  if item_id != response["Item"]["Id"]:
    item_id = response["Item"]["Id"]
    requests.post(url_send_photo, data=data_new, files={"photo": image})


def switch_case(argument):
  switcher = {
    "playback.start": send_message,
    "playback.stop": send_message,
    "playback.pause": send_message,
    "playback.unpause": send_message,
    "library.new": lib_new,
    "library.deleted": send_message,
    "item.markunplayed": marked,
    "item.markplayed": marked,
    "system.updateavailable": update,
    "user.authenticationfailed": send_message,
    "user.authenticated": send_message,
    "system.serverrestartrequired": send_message,
    "plugins.pluginuninstalled": send_message,
    "plugins.plugininstalled": send_message,
    'item.rate': rate,
  }
  return switcher.get(argument, "")


@app.route("/webhook", methods=["POST"])
def webhook():
  global list_id, response, send_id, token
  if request.method == "POST":
    response = request.json
    get_event_now = response["Event"]
    admin_id = get_admins()
    if admin_id is not None:
      for i in range(len(admin_id)):
        send_id = admin_id[i]
        print(get_event_now)
        arg_check = (
          "playback.start",
          "playback.stop",
          "playback.pause",
          "playback.unpause",
          "library.new",
          "library.deleted",
          "item.markunplayed",
          "item.markplayed",
          "system.updateavailable",
          "user.authenticationfailed",
          "user.authenticated",
          "system.serverrestartrequired",
          "plugins.pluginuninstalled",
          "plugins.plugininstalled",
          'item.rate',
        )
        if get_event_now.startswith(arg_check):
          switch_case(get_event_now)()
        else:
          send_message()
    user_id = get_users()
    if user_id is not None:
      for i in range(len(user_id)):
        send_id = user_id[i]
        arg_check = ("library.new", "library.deleted")
        if get_event_now.startswith(arg_check):
          switch_case(get_event_now)()
    return "success", 200
  else:
    abort(400)


if __name__ == "__main__":
  app.run()
