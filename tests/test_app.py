"""Тесты устойчивости и CORS для Flask API."""

import sys
from unittest.mock import patch, MagicMock
import importlib
import os
import logging
import requests
sys.path.append('.')

sys.path.append('api')
import app as app_module
flask_app = app_module.app


def _ok_resp():
    resp = MagicMock()
    resp.json.return_value = {"routes": ["ok"]}
    resp.raise_for_status.return_value = None
    return resp


def _error_resp(status=400):
    resp = MagicMock()
    resp.json.return_value = {"code": "InvalidQuery"}
    resp.status_code = status
    def raise_err():
        raise requests.HTTPError(response=resp)
    resp.raise_for_status.side_effect = raise_err
    return resp


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_route(mock_get):
    client = flask_app.test_client()
    r = client.get('/route?start=1,1&end=2,2')
    assert r.status_code == 200
    assert r.get_json() == {"routes": ["ok"]}


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_cors_header(mock_get):
    client = flask_app.test_client()
    r = client.get('/route?start=1,1&end=2,2', headers={'Origin': 'http://ex.com'})
    assert r.headers.get('Access-Control-Allow-Origin') == '*'


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_stability(mock_get):
    client = flask_app.test_client()
    for _ in range(10):
        r = client.get('/route?start=1,1&end=2,2')
        assert r.status_code == 200


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_table(mock_get):
    client = flask_app.test_client()
    r = client.get('/table?points=1,1;2,2')
    assert r.status_code == 200


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_nearest(mock_get):
    client = flask_app.test_client()
    r = client.get('/nearest?point=1,1')
    assert r.status_code == 200


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_match(mock_get):
    client = flask_app.test_client()
    r = client.get('/match?points=1,1;2,2')
    assert r.status_code == 200


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_trip(mock_get):
    client = flask_app.test_client()
    r = client.get('/trip?points=1,1;2,2')
    assert r.status_code == 200


@patch('routing.router.requests.get', return_value=_error_resp())
def test_error_forwarding(mock_get):
    client = flask_app.test_client()
    r = client.get('/trip?points=1,1;2,2')
    assert r.status_code == 400
    assert r.get_json() == {"code": "InvalidQuery"}


def test_run_app_port(monkeypatch):
    monkeypatch.setenv('PORT', '1234')
    app_reloaded = importlib.reload(app_module)
    with patch.object(app_reloaded.app, 'run') as mock_run:
        app_reloaded.run_app()
        mock_run.assert_called_with(host='0.0.0.0', port=1234)


@patch('app.app.run')
def test_run_app_logging_setup(mock_run):
    root = logging.getLogger()
    werk = logging.getLogger('werkzeug')
    old_root_handlers = root.handlers[:]
    old_root_level = root.level
    old_werk_handlers = werk.handlers[:]
    old_werk_level = werk.level
    root.handlers = []
    werk.handlers = []
    try:
        app_module.run_app()
        assert root.level == logging.INFO
        assert werk.level == logging.INFO
        assert any(isinstance(h, logging.StreamHandler) and h.stream is sys.stdout for h in root.handlers)
    finally:
        root.handlers = old_root_handlers
        root.setLevel(old_root_level)
        werk.handlers = old_werk_handlers
        werk.setLevel(old_werk_level)


