#!/bin/sh
set -e
# Запуск OSRM и обёртки Flask
osrm-routed --algorithm "${OSRM_ALGORITHM:-ch}" \
    --max-table-size "${OSRM_MAX_TABLE_SIZE:-800}" \
    --max-matching-size "${OSRM_MAX_MATCHING_SIZE:-100}" \
    --port 5001 /data/odessa_oblast.osrm &
exec python3 /app/app.py
