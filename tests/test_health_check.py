"""Тесты скрипта комплексной проверки сервиса."""

from unittest.mock import MagicMock, patch

import requests

import scripts.health_check as health


def test_check_data_files_reports_missing_and_existing(tmp_path):
    existing = tmp_path / "odessa_oblast.osm.pbf"
    existing.write_text("data")
    results = health.check_data_files(['odessa_oblast.osm.pbf', 'absent.pbf'], base_dir=tmp_path)
    assert results == [
        {'path': str(existing), 'status': 'ok'},
        {'path': str(tmp_path / 'absent.pbf'), 'status': 'missing'}
    ]


def test_check_osrm_status_success_json():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.ok = True
    fake_response.json.return_value = {'routes': []}
    with patch('requests.get', return_value=fake_response) as mock_get:
        result = health.check_osrm_status('http://example.com/osrm')
    mock_get.assert_called_once()
    assert result['status'] == 'ok'
    assert result['status_code'] == 200
    assert result['payload'] == {'routes': []}


def test_check_osrm_status_unreachable():
    with patch('requests.get', side_effect=requests.RequestException('boom')):
        result = health.check_osrm_status('http://example.com/osrm')
    assert result['status'] == 'unreachable'
    assert 'boom' in result['error']


def test_run_checks_uses_env(monkeypatch):
    monkeypatch.setenv('OSRM_URL', 'http://env-osrm')
    with patch('scripts.health_check.check_osrm_status', return_value={'status': 'ok'}) as mock_status:
        with patch('scripts.health_check.check_data_files', return_value=[{'path': 'x', 'status': 'ok'}]):
            result = health.run_checks()
    mock_status.assert_called_once_with('http://env-osrm')
    assert result == {
        'osrm_url': 'http://env-osrm',
        'osrm': {'status': 'ok'},
        'data': [{'path': 'x', 'status': 'ok'}]
    }
