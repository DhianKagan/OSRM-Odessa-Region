"""Тесты устойчивости и CORS для Flask API."""

import sys
from unittest.mock import patch, MagicMock

sys.path.append('api')
from app import app


def _mock_resp():
    resp = MagicMock()
    resp.json.return_value = {"routes": ["ok"]}
    resp.raise_for_status.return_value = None
    return resp


@patch('app.requests.get', return_value=_mock_resp())
def test_route(mock_get):
    client = app.test_client()
    r = client.get('/route?start=1,1&end=2,2')
    assert r.status_code == 200
    assert r.get_json() == {"routes": ["ok"]}


@patch('app.requests.get', return_value=_mock_resp())
def test_cors_header(mock_get):
    client = app.test_client()
    r = client.get('/route?start=1,1&end=2,2', headers={'Origin': 'http://ex.com'})
    assert r.headers.get('Access-Control-Allow-Origin') == '*'


@patch('app.requests.get', return_value=_mock_resp())
def test_stability(mock_get):
    client = app.test_client()
    for _ in range(10):
        r = client.get('/route?start=1,1&end=2,2')
        assert r.status_code == 200

