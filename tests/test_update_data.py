"""Тесты для скрипта обновления данных."""

import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append('scripts')
import update_data as upd


@patch('update_data.requests.get')
def test_download_map(mock_get, tmp_path):
    mock_resp = MagicMock()
    mock_resp.iter_content.return_value = [b'data']
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    dest = tmp_path / 'map.pbf'
    path = upd.download_map('http://ex.com/map.pbf', dest=str(dest))
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        assert f.read() == b'data'


@patch('update_data.subprocess.check_call')
def test_prepare_osrm(mock_call, tmp_path):
    pbf = tmp_path / 'map.osm.pbf'
    pbf.touch()
    upd.prepare_osrm(str(pbf))
    base = str(pbf).replace('.osm.pbf', '.osrm')
    mock_call.assert_any_call(['osrm-extract', '-p', '/opt/car.lua', str(pbf)])
    mock_call.assert_any_call(['osrm-partition', base])
    mock_call.assert_any_call(['osrm-customize', base])
