# OSRM Odessa

This repository provides a Docker container setup for an OSRM service using data for the Odessa region. It can be built and run locally or deployed via GitHub Codespaces and Railway.

## Repository Structure
```
osrm-odessa/
├── api/
│   ├── app.py
│   └── requirements.txt
├── data/
│   └── odessa_oblast.osm.pbf
├── Dockerfile
├── .stxxl
├── .gitignore
└── README.md
```

The `data` directory should contain the `odessa_oblast.osm.pbf` map file downloaded from [Geofabrik](https://download.geofabrik.de/). The `.stxxl` file is required for disk-based caching during preprocessing and should contain:

```
disk=/tmp/stxxl,10G,syscall
```

Both `.stxxl` and the map file are ignored via `.gitignore`.

## Usage
### Build and Run Locally
```
docker build -t osrm-odessa .
docker run -d -p 5000:5000 osrm-odessa
```
Then query the service:
```
curl "http://localhost:5000/route/v1/driving/30.7233,46.4825;30.7326,46.4775?overview=false"
```

### Run the Simple API Wrapper
Install dependencies and start the Flask app which proxies requests to the OSRM service:
```
pip install -r api/requirements.txt
python api/app.py
```
The `OSRM_URL` environment variable can be used to point the wrapper to a remote OSRM instance.

### Пример fetch
Запустить сервер и открыть `http://localhost:8080/` в браузере. На странице расположен
пример JavaScript, выполняющий `fetch` к API и выводящий ответ.

### Deploy on Railway
1. Create a new Railway project and connect this repository.
2. Ensure the `PORT` environment variable is set to `5000`.
3. Deploy the project and use the generated URL to query the service.

### Notes
- Replace `car.lua` with other profiles (e.g., `foot.lua`, `bicycle.lua`) if needed.
- Update `odessa_oblast.osm.pbf` periodically for fresh routing data.
