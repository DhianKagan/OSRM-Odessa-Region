"""Тесты для модуля routing.router."""

from unittest.mock import patch, MagicMock
import importlib
import sys

sys.path.append('.')

import routing.router as router_module


def _mock_resp():
    resp = MagicMock()
    resp.json.return_value = {"ok": True}
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
