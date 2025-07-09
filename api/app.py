"""Простая обёртка Flask для обращений к OSRM."""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)
OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')

# Конфигурация логгера, чтобы сообщения запуска сервера не попадали в error.
logging.getLogger('werkzeug').setLevel(logging.INFO)


@app.route('/')
def index():
    """Отдаёт пример использования API."""
    return app.send_static_file('index.html')

@app.route('/route')
def route():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end required'}), 400
    url = "{}/route/v1/driving/{};{}?overview=false".format(OSRM_URL, start, end)
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 502

def run_app() -> None:
    """Запускает сервер, учитывая переменную PORT."""
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_app()
