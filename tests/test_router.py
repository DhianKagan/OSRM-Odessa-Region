"""Тесты для модуля routing.router."""

from unittest.mock import patch, MagicMock
import importlib
import sys

sys.path.append('.')

import routing.router as router_module


def _mock_resp():
    resp = MagicMock()
    resp.json.return_value = {"code": "Ok", "routes": [{}]}
    resp.raise_for_status.return_value = None
    return resp


def test_route_call_builds_points():
    router = router_module.Router("http://example.com/")
    with patch('routing.router.requests.get', return_value=_mock_resp()) as mock_get:
        router.route('1,1', '2,2')
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == 'http://example.com/route/v1/driving/1,1;2,2'
        assert kwargs['params']['overview'] == 'false'


def test_route_with_via_points():
    router = router_module.Router("http://example.com")
    with patch('routing.router.requests.get', return_value=_mock_resp()) as mock_get:
        router.route('1,1', '4,4', via=['2,2', '3,3'], steps='true')
        args, kwargs = mock_get.call_args
        assert args[0].endswith('/route/v1/driving/1,1;2,2;3,3;4,4')
        assert kwargs['params']['steps'] == 'true'


def test_route_fallback_to_nearest_points():
    router = router_module.Router("http://example.com")

    route_responses = iter([
        {"code": "NoRoute", "routes": []},
        {"code": "Ok", "routes": [{"distance": 1000.0}], "waypoints": []}
    ])
    nearest_responses = iter([
        {"code": "Ok", "waypoints": [
            {"location": [1.1, 2.2]},
            {"location": [1.2, 2.3]}
        ]},
        {"code": "Ok", "waypoints": [
            {"location": [3.3, 4.4]}
        ]}
    ])

    def fake_get(url, params=None, timeout=None):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.status_code = 200
        if '/route/v1/driving/' in url:
            payload = next(route_responses)
        else:
            payload = next(nearest_responses)
        resp.json.return_value = payload
        return resp

    with patch('routing.router.requests.get', side_effect=fake_get) as mock_get:
        result = router.route('1,1', '2,2')

        assert result['code'] == 'Ok'
        assert result['routes']

        first_route_call = mock_get.call_args_list[0]
        assert first_route_call.args[0].endswith('/route/v1/driving/1,1;2,2')

        first_nearest_call = mock_get.call_args_list[1]
        assert first_nearest_call.args[0].endswith('/nearest/v1/driving/1,1')
        assert first_nearest_call.kwargs['params']['number'] == '5'

        second_nearest_call = mock_get.call_args_list[2]
        assert second_nearest_call.args[0].endswith('/nearest/v1/driving/2,2')
        assert second_nearest_call.kwargs['params']['number'] == '5'

        fallback_route_call = mock_get.call_args_list[3]
        assert fallback_route_call.args[0].endswith('/route/v1/driving/1.100000,2.200000;3.300000,4.400000')


def test_route_returns_original_when_fallback_not_possible():
    router = router_module.Router("http://example.com")

    route_responses = iter([
        {"code": "NoRoute", "routes": []}
    ])
    nearest_responses = iter([
        {"code": "Error", "waypoints": []}
    ])

    def fake_get(url, params=None, timeout=None):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.status_code = 200
        if '/route/v1/driving/' in url:
            payload = next(route_responses)
        else:
            payload = next(nearest_responses)
        resp.json.return_value = payload
        return resp

    with patch('routing.router.requests.get', side_effect=fake_get) as mock_get:
        result = router.route('1,1', '2,2')

        assert result['code'] == 'NoRoute'
        assert mock_get.call_args_list[1].args[0].endswith('/nearest/v1/driving/1,1')
        assert len(mock_get.call_args_list) == 2


def test_route_points_direct_call():
    router = router_module.Router("http://example.com")
    with patch('routing.router.requests.get', return_value=_mock_resp()) as mock_get:
        router.route_points('1,1;2,2', annotations='false')
        args, kwargs = mock_get.call_args
        assert args[0].endswith('/route/v1/driving/1,1;2,2')
        assert kwargs['params']['overview'] == 'false'
        assert kwargs['params']['annotations'] == 'false'


def test_set_algorithm():
    router = router_module.Router()
    router.set_algorithm('mld')
    assert router.algorithm == 'mld'


def test_default_algorithm(monkeypatch):
    monkeypatch.delenv('OSRM_ALGORITHM', raising=False)
    importlib.reload(router_module)
    router = router_module.Router()
    assert router.algorithm == 'mld'
