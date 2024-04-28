# Emby-Telegram-Notifier
simple webhook server to emby Telegram notification

### Features
 * Integrates with the webhook plugin.
 * Telegram notifications with media images and summary when a new movie or series is added to Emby.

## Create a new telegram-bot
**1** - Search Botfather in telegram. <br>
**2** - Send command /newbot to Botfather. <br>
**3** - Give the Telegram bot a name. <br>
**4** - Give the Telegram bot a unique username, it must end in "bot". <br>
**5** - Save the Telegram bot's access token, we will use it later in the env configuration. <br>
**6** - Get your chat ID by starting a chat with your bot, sending a message and then visiting https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates to find the chat ID in the returned JSON.

## Run the webhook-server
**1** - Clone this repo. <br>
**2** - Run the server with docker:<br>
docker run:
```
docker run -d --restart=always -v </path/to/clone/dir>:/App -e TID=<telegram-id1> <telegram-id2> -e TT=<telegram-bot-token> -p 5000:5000 yoas1/flask-base:1.0
```
docker compose:
```
version: "3.5"
services:
  webhook-server:
    container_name: webhook-server
    image: yoas1/flask-base:1.0
    volumes:
      - </path/to/clone/dir>:/App
    ports:
      - 5000:5000
    environment:
      TID: <telegram-id1> <telegram-id2>
      TT: <telegram-bot-token>
    restart: always
```
* yoas1/flask-base [Dockerfile](https://github.com/Yoas1/dockerfiles/blob/main/flask_base_docker_image/Dockerfile).<br>

**3** - Create emby/jellyfin notification:<br>
* Go to Settings --> Notifications
* Add Notifications --> select **Webhook**:
    * Name: name to your notification
    * Url: http://server-ip:5000/webhook
    * Request content type: application/json
    * Events: select your send events to telegram


## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for new features, bug fixes, or improvements.
