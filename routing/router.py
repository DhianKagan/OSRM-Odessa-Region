"""Обёртка над HTTP API OSRM с возможностью смены алгоритма."""

import os

import requests


OSRM_URL = os.environ.get('OSRM_URL', 'http://localhost:5000')
NEAREST_CANDIDATE_LIMIT = 5


class Router:
    """Клиент OSRM с выбором алгоритма."""

    def __init__(self, base_url=OSRM_URL):
        self.base_url = base_url.rstrip('/')
        self.algorithm = os.environ.get('OSRM_ALGORITHM', 'mld')

    def set_algorithm(self, name):
        """Изменить алгоритм маршрутизации."""
        self.algorithm = name

    def _request(self, path, params=None):
        params = params or {}
        url = "{}{}".format(self.base_url, path)
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def route_points(self, points, **params):
        """Строит маршрут по заранее собранной строке координат."""

        query = {'overview': 'false'}

        query.update(params)
        path = "/route/v1/driving/{}".format(points)
        return self._request(path, query)

    def route(self, start, end, via=None, **params):
        """Строит маршрут между стартом и финишем с необязательными via-точками."""
        coordinates = [start]
        if via:
            coordinates.extend(via)
        coordinates.append(end)
        points = ';'.join(coordinates)
        response = self.route_points(points, **params)
        if self._is_route_success(response):
            return response

        fallback_response = self._route_with_nearest_points(start, end, via, params)
        if fallback_response is not None:
            return fallback_response
        return response

    @staticmethod
    def _is_route_success(response):
        return (
            isinstance(response, dict)
            and response.get('code') == 'Ok'
            and bool(response.get('routes'))
        )

    @staticmethod
    def _format_location(location):
        if not location or len(location) < 2:
            return None
        lon, lat = location[0], location[1]
        return "{:.6f},{:.6f}".format(lon, lat)

    def _nearest_candidates(self, point):
        response = self.nearest(point, number=str(NEAREST_CANDIDATE_LIMIT))
        if response.get('code') != 'Ok':
            return []

        candidates = []
        seen = set()
        for waypoint in response.get('waypoints') or []:
            formatted = self._format_location(waypoint.get('location'))
            if formatted and formatted not in seen:
                candidates.append(formatted)
                seen.add(formatted)
        return candidates

    def _route_with_nearest_points(self, start, end, via, params):
        start_candidates = self._nearest_candidates(start)
        if not start_candidates:
            return None

        end_candidates = self._nearest_candidates(end)
        if not end_candidates:
            return None

        via_points = list(via) if via else []
        for start_point in start_candidates:
            for end_point in end_candidates:
                coordinates = [start_point]
                if via_points:
                    coordinates.extend(via_points)
                coordinates.append(end_point)
                points = ';'.join(coordinates)
                response = self.route_points(points, **params)
                if self._is_route_success(response):
                    return response
        return None


    def table(self, points, **params):
        path = "/table/v1/driving/{}".format(points)
        return self._request(path, params)

    def nearest(self, point, **params):
        path = "/nearest/v1/driving/{}".format(point)
        return self._request(path, params)

    def match(self, points, **params):
        path = "/match/v1/driving/{}".format(points)
        return self._request(path, params)

    def trip(self, points, **params):

        path = "/trip/v1/driving/{}".format(points)
        return self._request(path, params)

    def rebuild(self):
        """Быстрая перестройка CH с учётом обновлённого трафика."""
        os.system("osrm-customize /data/odessa_oblast.osrm")
