FROM osrm/osrm-backend

WORKDIR /data

COPY data/odessa_oblast.osm.pbf /data/
COPY .stxxl /root/.stxxl

RUN osrm-extract -p /opt/car.lua /data/odessa_oblast.osm.pbf && \
    osrm-partition /data/odessa_oblast.osrm && \
    osrm-customize /data/odessa_oblast.osrm

EXPOSE 5000

CMD ["osrm-routed", "--algorithm", "mld", "/data/odessa_oblast.osrm"]
