"""Обёртка над HTTP API OSRM с возможностью смены алгоритма."""

from __future__ import annotations

import os
from typing import Optional, Sequence, Dict, Any

import requests


OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')


class Router:
    """Клиент OSRM с выбором алгоритма."""

    def __init__(self, base_url: str = OSRM_URL):
        self.base_url = base_url.rstrip('/')
        self.algorithm = os.environ.get('OSRM_ALGORITHM', 'mld')

    def set_algorithm(self, name: str) -> None:
        """Изменить алгоритм маршрутизации."""
        self.algorithm = name

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> dict:
        params = params or {}
        url = "{}{}".format(self.base_url, path)
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def route_points(self, points: str, **params: Any) -> dict:
        """Строит маршрут по заранее собранной строке координат."""
        query: Dict[str, Any] = {'overview': 'false'}
        query.update(params)
        path = "/route/v1/driving/{}".format(points)
        return self._request(path, query)

    def route(self, start: str, end: str, via: Optional[Sequence[str]] = None, **params: Any) -> dict:
        """Строит маршрут между стартом и финишем с необязательными via-точками."""
        coordinates = [start]
        if via:
            coordinates.extend(via)
        coordinates.append(end)
        points = ';'.join(coordinates)
        return self.route_points(points, **params)

    def table(self, points: str, **params: Any) -> dict:
        path = "/table/v1/driving/{}".format(points)
        return self._request(path, params)

    def nearest(self, point: str, **params: Any) -> dict:
        path = "/nearest/v1/driving/{}".format(point)
        return self._request(path, params)

    def match(self, points: str, **params: Any) -> dict:
        path = "/match/v1/driving/{}".format(points)
        return self._request(path, params)

    def trip(self, points: str, **params: Any) -> dict:
        path = "/trip/v1/driving/{}".format(points)
        return self._request(path, params)

    def rebuild(self) -> None:
        """Быстрая перестройка CH с учётом обновлённого трафика."""
        os.system("osrm-customize /data/odessa_oblast.osrm")
