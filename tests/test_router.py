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


def test_route_call():
    r = router_module.Router("http://example.com")
    with patch('routing.router.requests.get', return_value=_mock_resp()) as mock_get:
        r.route('1,1', '2,2')
        mock_get.assert_called_once()


def test_set_algorithm():
    r = router_module.Router()
    r.set_algorithm('mld')
    assert r.algorithm == 'mld'


def test_default_algorithm(monkeypatch):
    monkeypatch.delenv('OSRM_ALGORITHM', raising=False)
    importlib.reload(router_module)
    r = router_module.Router()
    assert r.algorithm == 'mld'
