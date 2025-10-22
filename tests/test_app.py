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
    resp.json.return_value = {"code": "Ok", "routes": ["ok"]}
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
    assert r.get_json() == {"code": "Ok", "routes": ["ok"]}


@patch('routing.router.requests.get', return_value=_ok_resp())
def test_route_with_via_param(mock_get):
    client = flask_app.test_client()
    r = client.get('/route?start=1,1&end=4,4&via=2,2&via=3,3&overview=full')
    assert r.status_code == 200
    _, kwargs = mock_get.call_args
    assert kwargs['params']['overview'] == 'full'


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


def _summary_route_response():
    return {
        'code': 'Ok',
        'routes': [{
            'distance': 1000.0,
            'duration': 120.0,
            'legs': [{
                'distance': 1000.0,
                'duration': 120.0,
                'summary': 'Тестовый участок',
                'steps': []
            }]
        }],
        'waypoints': [
            {'name': 'Старт', 'location': [30.0, 46.0]},
            {'name': 'Финиш', 'location': [31.0, 46.5]}
        ]
    }


@patch('app.router.route', autospec=True)
def test_route_summary_endpoint(mock_route):
    mock_route.return_value = _summary_route_response()
    client = flask_app.test_client()
    response = client.get('/route/summary?start=1,1&end=2,2')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['summary']['distance_km'] == 1.0
    assert payload['summary']['duration_min'] == 2.0
    assert 'route' in payload
    assert mock_route.call_args.kwargs['steps'] == 'true'


@patch('app.router.route', autospec=True)
def test_route_summary_with_points_param(mock_route):
    mock_route.return_value = _summary_route_response()
    client = flask_app.test_client()
    response = client.get('/route/summary?points=1,1;2,2;3,3&steps=false')
    assert response.status_code == 200
    assert mock_route.call_args.kwargs['steps'] == 'false'
    assert mock_route.call_args.kwargs['via'] == ['2,2']


def test_route_summary_validation():
    client = flask_app.test_client()
    response = client.get('/route/summary')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'points or start/end required'}


