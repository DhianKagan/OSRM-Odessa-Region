"""Обёртка над HTTP API OSRM с возможностью смены алгоритма."""

import os
from typing import Optional
import requests

OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')

class Router:
    """Клиент OSRM с выбором алгоритма."""

    def __init__(self, base_url: str = OSRM_URL):
        self.base_url = base_url
        self.algorithm = os.environ.get('OSRM_ALGORITHM', 'mld')

    def set_algorithm(self, name: str) -> None:
        """Изменить алгоритм маршрутизации."""
        self.algorithm = name

    def _request(self, path: str, params: Optional[dict] = None) -> dict:
        params = params or {}
        url = "{}{}".format(self.base_url, path)
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def route(self, start: str, end: str) -> dict:
        path = "/route/v1/driving/{};{}?overview=false".format(start, end)
        return self._request(path)

    def table(self, points: str, **params) -> dict:
        path = "/table/v1/driving/{}".format(points)
        return self._request(path, params)

    def nearest(self, point: str, **params) -> dict:
        path = "/nearest/v1/driving/{}".format(point)
        return self._request(path, params)

    def match(self, points: str, **params) -> dict:
        path = "/match/v1/driving/{}".format(points)
        return self._request(path, params)

    def trip(self, points: str, **params) -> dict:
        path = "/trip/v1/driving/{}".format(points)
        return self._request(path, params)

    def rebuild(self) -> None:
        """Быстрая перестройка CH с учётом обновлённого трафика."""
        os.system("osrm-customize /data/odessa_oblast.osrm")
