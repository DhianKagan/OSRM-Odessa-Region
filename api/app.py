"""Простая обёртка Flask для обращений к OSRM."""

import os
import logging
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from routing.router import Router

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)
OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')
router = Router(OSRM_URL)


def _call_osrm(method, *args, **kwargs):
    """Вызывает OSRM и корректно передаёт код ошибки."""
    try:
        data = method(*args, **kwargs)
        return jsonify(data), 200
    except requests.HTTPError as exc:
        resp = exc.response
        try:
            payload = resp.json()
        except ValueError:
            payload = {'error': resp.text}
        return jsonify(payload), resp.status_code
    except requests.RequestException as exc:
        return jsonify({'error': str(exc)}), 502

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
    return _call_osrm(router.route, start, end)


@app.route('/table')
def table():
    """Передаёт запрос к сервису table OSRM."""
    coords = request.args.get('points')
    if not coords:
        return jsonify({'error': 'points required'}), 400
    params = request.args.to_dict(flat=True)
    params.pop('points', None)
    return _call_osrm(router.table, coords, **params)


@app.route('/nearest')
def nearest():
    """Передаёт запрос к сервису nearest OSRM."""
    coord = request.args.get('point')
    if not coord:
        return jsonify({'error': 'point required'}), 400
    params = request.args.to_dict(flat=True)
    params.pop('point', None)
    return _call_osrm(router.nearest, coord, **params)


@app.route('/match')
def match():
    """Передаёт запрос к сервису match OSRM."""
    coords = request.args.get('points')
    if not coords:
        return jsonify({'error': 'points required'}), 400
    params = request.args.to_dict(flat=True)
    params.pop('points', None)
    return _call_osrm(router.match, coords, **params)


@app.route('/trip')
def trip():
    """Передаёт запрос к сервису trip OSRM."""
    coords = request.args.get('points')
    if not coords:
        return jsonify({'error': 'points required'}), 400
    params = request.args.to_dict(flat=True)
    params.pop('points', None)
    return _call_osrm(router.trip, coords, **params)

def run_app() -> None:
    """Запускает сервер, учитывая переменную PORT."""
    port = int(os.environ.get('PORT', '5000'))
    handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_app()
