"""Скрипт обновления карты Одессы."""

import os
import subprocess
from typing import Optional

import requests

DEFAULT_URL = "https://download.geofabrik.de/europe/ukraine/odessa-oblast-latest.osm.pbf"


def download_map(url: str = DEFAULT_URL, dest: str = "data/odessa_oblast.osm.pbf") -> str:
    """Скачивает карту и сохраняет её в указанное место."""
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest


def prepare_osrm(pbf_path: str = "data/odessa_oblast.osm.pbf") -> None:
    """Готовит файлы OSRM для маршрутизации."""
    base = pbf_path.replace(".osm.pbf", ".osrm")
    subprocess.check_call(["osrm-extract", "-p", "/opt/car.lua", pbf_path])
    subprocess.check_call(["osrm-partition", base])
    subprocess.check_call(["osrm-customize", base])


if __name__ == "__main__":
    path = download_map()
    prepare_osrm(path)
