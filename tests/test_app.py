"""Тесты устойчивости и CORS для Flask API."""

import sys
from unittest.mock import patch, MagicMock
import importlib
import os

sys.path.append('api')
import app as app_module
flask_app = app_module.app


def _mock_resp():
    resp = MagicMock()
    resp.json.return_value = {"routes": ["ok"]}
    resp.raise_for_status.return_value = None
    return resp


@patch('app.requests.get', return_value=_mock_resp())
def test_route(mock_get):
    client = flask_app.test_client()
    r = client.get('/route?start=1,1&end=2,2')
    assert r.status_code == 200
    assert r.get_json() == {"routes": ["ok"]}


@patch('app.requests.get', return_value=_mock_resp())
def test_cors_header(mock_get):
    client = flask_app.test_client()
    r = client.get('/route?start=1,1&end=2,2', headers={'Origin': 'http://ex.com'})
    assert r.headers.get('Access-Control-Allow-Origin') == '*'


@patch('app.requests.get', return_value=_mock_resp())
def test_stability(mock_get):
    client = flask_app.test_client()
    for _ in range(10):
        r = client.get('/route?start=1,1&end=2,2')
        assert r.status_code == 200


def test_run_app_port(monkeypatch):
    monkeypatch.setenv('PORT', '1234')
    app_reloaded = importlib.reload(app_module)
    with patch.object(app_reloaded.app, 'run') as mock_run:
        app_reloaded.run_app()
        mock_run.assert_called_with(host='0.0.0.0', port=1234)


def test_logging_level():
    """Проверяет уровень логирования werkzeug."""
    import logging
    app_reloaded = importlib.reload(app_module)
    assert logging.getLogger('werkzeug').level <= logging.INFO

