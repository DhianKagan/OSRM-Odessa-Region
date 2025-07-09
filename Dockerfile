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
RUN apt-get update \ 
    && apt-get install -y python3 python3-pip \ 
    && rm -rf /var/lib/apt/lists/*
COPY api /app
COPY start.sh /start.sh
RUN pip3 install --no-cache-dir -r /app/requirements.txt
ENV OSRM_URL=http://localhost:5001
EXPOSE 5000
CMD ["/start.sh"]
