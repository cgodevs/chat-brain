from flask import Flask, request, jsonify
from flask_cors import CORS
from tools import *

app = Flask(__name__)
CORS(app,
     resources={r"/*": {
         "origins": "http://localhost:3000",  # Be specific with origin for requests with credentials
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True  # Enable credentials support
     }})


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
    app.run(debug=True, host='0.0.0.0', port=5000)