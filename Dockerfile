# Build OSRM data
FROM osrm/osrm-backend as builder
WORKDIR /data
COPY data/odessa_oblast.osm.pbf /data/
COPY .stxxl /root/.stxxl
RUN osrm-extract -p /opt/car.lua /data/odessa_oblast.osm.pbf && \
    osrm-partition /data/odessa_oblast.osrm && \
    osrm-customize /data/odessa_oblast.osrm

# Final image with API
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /data /data
COPY api /app
COPY start.sh /start.sh
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV OSRM_URL=http://localhost:5001
EXPOSE 5000
CMD ["/start.sh"]
