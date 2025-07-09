#!/bin/sh
set -e
# Запуск OSRM и обёртки Flask
osrm-routed --algorithm mld --port 5001 /data/odessa_oblast.osrm &
exec python3 /app/app.py
