"""network_speed_monitor_script"""

import os
import time
from datetime import datetime

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from ping3 import ping as run_ping_test
import speedtest

# Load environment variables
load_dotenv(override=True)

# Constants from environment variables
SPEEDTEST_INTERVAL = int(os.getenv("speedtest_interval", "300"))
LATENCY_INTERVAL = int(os.getenv("latency_interval", "30"))
LATENCY_SERVERS = os.getenv("latency_servers", "").split()
INFLUX_URL = os.getenv("influx_url")
INFLUX_TOKEN = os.getenv("influx_token")
INFLUX_BUCKET = os.getenv("influx_bucket")
INFLUX_ORG = os.getenv("influx_org")


def log(severity, msg):
    """Print a log message including a timestamp"""
    print(f"{datetime.now().isoformat()}, level={severity}, msg={msg}")


def print_env_variables():
    """Print the environment variables for verification on startup."""
    print("Environment Variables:")
    print(f"speedtest_interval: {SPEEDTEST_INTERVAL}")
    print(f"latency_interval: {LATENCY_INTERVAL}")
    print(f"latency_servers: {LATENCY_SERVERS}")
    print(f"influx_url: {INFLUX_URL}")
    print(f"influx_token: {'<hidden>' if INFLUX_TOKEN else 'None'}")
    print(f"influx_bucket: {INFLUX_BUCKET}")
    print(f"influx_org: {INFLUX_ORG}")
    print("----------------\n")


def run_speedtest():
    """Runs the speed test and returns download, upload speeds and ping."""
    try:
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download()
        s.upload()

        data = s.results.dict()
        return {
            "Download": round(data["download"] * 0.000001, 2),  # Convert to Mbps
            "Upload": round(data["upload"] * 0.000001, 2),  # Convert to Mbps
            "Ping": round(data.get("ping") or 0, 2),
        }
    except Exception as e:
        log("error", f"Error while performing speed test: {e}")
        return None


def run_latency_test():
    """Runs the latency test against provided servers and returns the latency in milliseconds."""
    if not LATENCY_SERVERS:
        log("warning", "No latency servers defined.")
        return {}

    latency_data = {}
    for server in LATENCY_SERVERS:
        try:
            result = run_ping_test(server)
        except Exception as e:
            log("error", f"Ping error for {server}: {e}")
            result = None
        if isinstance(result, float):
            latency_data[server] = round(result * 1000, 2)
    return latency_data


def store_data(influx_filter, influx_result, write_api):
    """Stores the given data to InfluxDB."""
    if not influx_result:
        log("error", f"No data to store for {influx_filter}.")
        return

    try:
        for key, value in influx_result.items():
            try:
                # ensure numeric value (Influx line protocol accepts floats by default)
                numeric = float(value)
            except Exception:
                log("error", f"Skipping non-numeric value {key}={value}")
                continue
            string = f"{influx_filter} {key}={numeric}"
            write_api.write(INFLUX_BUCKET, INFLUX_ORG, string)
        log("info", f"{influx_filter} data uploaded to InfluxDB.")
    except Exception as e:
        log("error", f"Could not store {influx_filter} data to InfluxDB: {e}")


def network_speed_monitor():
    """Runs the performance tests at the defined intervals and stores the results in InfluxDB."""

    # basic env validation
    missing = [
        k
        for k in ("INFLUX_URL", "INFLUX_TOKEN", "INFLUX_BUCKET", "INFLUX_ORG")
        if not globals().get(k)
    ]
    if missing:
        log("error", f"Missing required environment variables: {', '.join(missing)}")
        return

    print_env_variables()

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    last_speedtest_time = 0
    last_latency_test_time = 0

    try:
        while True:
            current_time = time.time()

            # Run speed test based on the speedtest interval
            if current_time - last_speedtest_time >= SPEEDTEST_INTERVAL:
                log("info", "Running speed test")
                speed_data = run_speedtest()
                if speed_data:
                    store_data("Speed", speed_data, write_api)
                last_speedtest_time = current_time

            # Run latency test based on the latency interval
            if current_time - last_latency_test_time >= LATENCY_INTERVAL:
                log("info", "Running latency test")
                latency_data = run_latency_test()
                if latency_data:
                    store_data("Latency", latency_data, write_api)
                last_latency_test_time = current_time

            time.sleep(1)
    except KeyboardInterrupt:
        log("info", "Stopping network monitor (KeyboardInterrupt).")
    finally:
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    network_speed_monitor()
