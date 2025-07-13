"""Обёртка над HTTP API OSRM с возможностью смены алгоритма."""

import os
import requests

OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')

class Router:
    """Клиент OSRM с выбором алгоритма."""

    def __init__(self, base_url: str = OSRM_URL):
        self.base_url = base_url
        self.algorithm = os.environ.get('OSRM_ALGORITHM', 'ch')

    def set_algorithm(self, name: str) -> None:
        """Изменить алгоритм маршрутизации."""
        self.algorithm = name

    def _request(self, path: str, params: dict | None = None) -> dict:
        params = params or {}
        url = f"{self.base_url}{path}"
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def route(self, start: str, end: str) -> dict:
        path = f"/route/v1/driving/{start};{end}?overview=false"
        return self._request(path)

    def table(self, points: str, **params) -> dict:
        path = f"/table/v1/driving/{points}"
        return self._request(path, params)

    def nearest(self, point: str, **params) -> dict:
        path = f"/nearest/v1/driving/{point}"
        return self._request(path, params)

    def match(self, points: str, **params) -> dict:
        path = f"/match/v1/driving/{points}"
        return self._request(path, params)

    def trip(self, points: str, **params) -> dict:
        path = f"/trip/v1/driving/{points}"
        return self._request(path, params)

    def rebuild(self) -> None:
        """Быстрая перестройка CH с учётом обновлённого трафика."""
        os.system("osrm-customize /data/odessa_oblast.osrm")
