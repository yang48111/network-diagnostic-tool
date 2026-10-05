import subprocess
import socket
import re

from analyzer import parse_ping_result

def get_wifi_raw_info():
    result = subprocess.run(
        [
            "netsh",
            "wlan",
            "show",
            "interfaces"
        ],
        capture_output=True,
        text=True,
        errors="replace"
    )

    return result.stdout

def get_wifi_info():
    output = get_wifi_raw_info()

    raw_data = {}

    for line in output.splitlines():
        line = line.strip()

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        raw_data[key.strip()] = value.strip()

    signal_text = raw_data.get(
        "Signal"
    )

    signal = None

    if signal_text:
        signal = int(
            signal_text.replace("%", "")
        )

    return {
        "state": raw_data.get("State"),
        "ssid": raw_data.get("SSID"),
        "bssid": raw_data.get("BSSID"),
        "radio_type": raw_data.get(
            "Radio type"
        ),
        "band": raw_data.get("Band"),
        "channel": raw_data.get(
            "Channel"
        ),
        "receive_rate": raw_data.get(
            "Receive rate (Mbps)"
        ),
        "transmit_rate": raw_data.get(
            "Transmit rate (Mbps)"
        ),
        "signal": signal
    }

def get_network_info():
    subprocess.run(
        ["ipconfig", "/all"]
    )


def run_ping(host, count=4):
    result = subprocess.run(
        [
            "ping",
            host,
            "-n",
            str(count)
        ],
        capture_output=True,
        text=True
    )

    data = parse_ping_result(
        result.stdout
    )

    data["host"] = host
    data["success"] = (
        result.returncode == 0
    )

    return data


def ping_once(host):
    result = subprocess.run(
        [
            "ping",
            host,
            "-n",
            "1",
            "-w",
            "1000"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    match = re.search(
        r"time[=<]\s*(\d+)ms",
        result.stdout,
        re.IGNORECASE
    )

    if match:
        return int(
            match.group(1)
        )

    return None


def get_default_gateway():
    result = subprocess.run(
        [
            "route",
            "print",
            "0.0.0.0"
        ],
        capture_output=True,
        text=True
    )

    lines = (
        result.stdout.splitlines()
    )

    for line in lines:
        parts = line.split()

        if len(parts) >= 3:
            if (
                parts[0] == "0.0.0.0"
                and
                parts[1] == "0.0.0.0"
            ):
                return parts[2]

    return None


def check_dns(domain):
    try:
        ip_address = (
            socket.gethostbyname(
                domain
            )
        )

        return {
            "success": True,
            "domain": domain,
            "ip": ip_address
        }

    except socket.gaierror:
        return {
            "success": False,
            "domain": domain,
            "ip": None
        }