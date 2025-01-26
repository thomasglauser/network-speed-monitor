## network-speed-monitor

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![Dependabot Updates](https://github.com/thomasglauser/network-speed-monitor/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/thomasglauser/network-speed-monitor/actions/workflows/dependabot/dependabot-updates)
[![CodeQL Advanced](https://github.com/thomasglauser/network-speed-monitor/actions/workflows/codeql.yml/badge.svg)](https://github.com/thomasglauser/network-speed-monitor/actions/workflows/codeql.yml)
[![Create and publish Docker image](https://github.com/thomasglauser/network-speed-monitor/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/thomasglauser/network-speed-monitor/actions/workflows/docker-publish.yml)

## Features

-   Monitoring of Download/Upload speeds (Via speedtest.net)
-   Monitoring of server latency
-   Everything is containerized
-   Simple configuration with docker-compose

## Demo

![Dashboard](https://github.com/thomasglauser/network-speed-monitor/raw/main/docs/images/dashboard.PNG)

## Deployment with Docker Compose

To deploy this project run

```bash
git clone https://github.com/thomasglauser/network-speed-monitor.git

cd network-speed-monitor
```

Create a `.env` file in the projects directory.

Add the following configuration:

```
[CONFIG]
# Those values define the interval in seconds for both speedtest and latency test.
speedtest_interval = 60
latency_interval = 10

# This addresses defines the servers which will be pinged, seperated with spaces!
# If a server isn't reacable, no value will be stored in the database!
latency_servers = google.com github.com

[INFLUX_DB]
# This is the address of the influxdb
influx_url = "http://influxdb:8086"

# This is the authentication token. If you need to change or set it initially, just rerun 'docker compose up -d --force-recreate --build' after it.
influx_token = 'api-token'

influx_bucket = test
influx_org = test

```

Now start the project with docker-compose

```
docker-compose up --force-recreate --build
```

If everything runs, access the InfluxDB web interface at http://localhost:8086

You will need to do some initial configuration and generate a token for authentication.

After you generated a token, copy and paste it in the .env file and rerun `docker compose up -d --force-recreate --build`.

Done!

## Contributing

Contributions are always welcome! Just open a Pull Request.

## License

[GNU General Public License v3.0](https://github.com/thomasglauser/network-speed-monitor/blob/main/LICENSE)
