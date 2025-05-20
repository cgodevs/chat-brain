from flask import Flask, request, jsonify
from tools import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Houston, we don\'t have a problem! :)'

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json(force=True)   # force=True will parse even if no Content-Type header
    message = data.get('message', '')
    ai_message = get_ai_message(message)
    return jsonify({
        'status': 'ok',
        'received': ai_message
    }), 200


if __name__ == '__main__':
    app.run()
