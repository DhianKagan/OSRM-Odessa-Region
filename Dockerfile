# Build OSRM data
FROM osrm/osrm-backend as builder
WORKDIR /data
COPY data/odessa_oblast.osm.pbf /data/
COPY .stxxl /root/.stxxl
RUN osrm-extract -p /opt/car.lua /data/odessa_oblast.osm.pbf && \
    osrm-partition /data/odessa_oblast.osrm && \
    osrm-customize /data/odessa_oblast.osrm

# Final image with API
FROM osrm/osrm-backend
WORKDIR /app
COPY --from=builder /data /data
# Debian Stretch архивирован; корректируем источники пакетов
RUN sed -i 's|deb.debian.org/debian|archive.debian.org/debian|g' /etc/apt/sources.list \
    && sed -i 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && sed -i '/stretch-updates/d' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*
COPY api /app
COPY routing /app/routing
COPY start.sh /start.sh
RUN pip3 install --no-cache-dir -r /app/requirements.txt
ENV OSRM_URL=http://localhost:5001
EXPOSE 5000
CMD ["/start.sh"]
