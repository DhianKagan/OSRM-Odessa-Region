"""Скрипт для комплексной проверки развёрнутого сервиса OSRM."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, List, Dict, Any

import requests


DEFAULT_SAMPLE_ROUTE = "46.4825,30.7233;46.4825,30.7233"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _normalize_base_url(base_url: str) -> str:
    """Удаляет завершающий слэш для корректной сборки URL."""
    return base_url[:-1] if base_url.endswith('/') else base_url


def check_data_files(required_paths: Iterable[str], base_dir: Path | None = None) -> List[Dict[str, Any]]:
    """Проверяет наличие обязательных файлов данных."""
    base = base_dir or Path.cwd()
    results: List[Dict[str, Any]] = []
    for rel_path in required_paths:
        path = base / rel_path
        results.append({
            'path': str(path),
            'status': 'ok' if path.exists() else 'missing'
        })
    return results


def check_osrm_status(base_url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Отправляет тестовый запрос к сервису OSRM и возвращает статус."""
    url = "{}/route/v1/driving/{}".format(_normalize_base_url(base_url), DEFAULT_SAMPLE_ROUTE)
    try:
        response = requests.get(url, params={'overview': 'false'}, timeout=timeout)
        result: Dict[str, Any] = {
            'status_code': response.status_code,
            'status': 'ok' if response.ok else 'error'
        }
        try:
            result['payload'] = response.json()
        except ValueError:
            result['payload'] = response.text
        return result
    except requests.RequestException as exc:
        return {
            'status': 'unreachable',
            'error': str(exc)
        }


def run_checks(base_url: str | None = None) -> Dict[str, Any]:
    """Выполняет полный набор проверок и возвращает структуру с результатами."""
    resolved_url = base_url or os.environ.get('OSRM_URL', 'http://localhost:5000')
    data_results = check_data_files(['data/odessa_oblast.osm.pbf'], base_dir=REPO_ROOT)
    osrm_result = check_osrm_status(resolved_url)
    return {
        'osrm_url': resolved_url,
        'osrm': osrm_result,
        'data': data_results
    }


def main() -> None:
    """Выводит результаты проверок в формате JSON."""
    results = run_checks()
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
