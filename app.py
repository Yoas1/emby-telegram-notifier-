from flask import Flask, request, abort
import emby_func
from os import environ

app = Flask(__name__)

t_id = environ['TID']
t_token = environ['TT']
list_id = emby_func.convert_list(t_id)


@app.route('/webhook', methods=['POST'])
def webhook():
    global list_id
    global t_token
    if request.method == 'POST':
        data = request.json
        for i in range(len(list_id)):
            send_id = list_id[i]
            emby_func.parser_send(data, send_id, t_token)
        return 'success', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run()