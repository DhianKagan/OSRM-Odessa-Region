import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')

@app.route('/route')
def route():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end required'}), 400
    url = f"{OSRM_URL}/route/v1/driving/{start};{end}?overview=false"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
