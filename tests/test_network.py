from unittest.mock import patch
import socket
import network

from network import (
    run_ping,
    ping_once,
    check_dns,
    get_default_gateway)

@patch("network.subprocess.run")
def test_run_ping_success(mock_run):
    mock_run.return_value.returncode = 0

    mock_run.return_value.stdout = """
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),

Minimum = 10ms, Maximum = 20ms, Average = 15ms
"""

    result = run_ping(
        "8.8.8.8"
    )

    assert result["success"] is True
    assert result["packet_loss"] == 0
    assert result["minimum"] == 10
    assert result["maximum"] == 20
    assert result["average"] == 15

@patch("network.subprocess.run")
def test_run_ping_failure(mock_run):
    mock_run.return_value.returncode = 1

    mock_run.return_value.stdout = """
Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
"""

    result = run_ping(
        "8.8.8.8"
    )

    assert result["success"] is False
    assert result["packet_loss"] == 100
    assert result["average"] is None

@patch("network.subprocess.run")
def test_run_ping_command(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = """
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),

Minimum = 10ms, Maximum = 20ms, Average = 15ms
"""

    run_ping(
        "google.com",
        count=5
    )

    mock_run.assert_called_once_with(
        [
            "ping",
            "google.com",
            "-n",
            "5"
        ],
        capture_output=True,
        text=True
    )

@patch("network.subprocess.run")
def test_ping_once_success(mock_run):
    mock_run.return_value.returncode = 0

    mock_run.return_value.stdout = """
Reply from 8.8.8.8: bytes=32 time=18ms TTL=117
"""

    result = ping_once(
        "8.8.8.8"
    )

    assert result == 18

@patch("network.subprocess.run")
def test_ping_once_timeout(mock_run):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stdout = ""

    result = ping_once(
        "8.8.8.8"
    )

    assert result is None

@patch("network.subprocess.run")
def test_ping_once_less_than_one_ms(
    mock_run
):
    mock_run.return_value.returncode = 0

    mock_run.return_value.stdout = """
Reply from 192.168.1.1: bytes=32 time<1ms TTL=64
"""

    result = ping_once(
        "192.168.1.1"
    )

    assert result == 1

@patch("network.socket.gethostbyname")
def test_check_dns_success(
    mock_gethostbyname
):
    mock_gethostbyname.return_value = (
        "142.250.1.1"
    )

    result = check_dns(
        "google.com"
    )

    assert result["success"] is True
    assert result["domain"] == "google.com"
    assert result["ip"] == "142.250.1.1"

@patch("network.socket.gethostbyname")
def test_check_dns_failure(
    mock_gethostbyname
):
    mock_gethostbyname.side_effect = (
        socket.gaierror
    )

    result = check_dns(
        "invalid.test"
    )

    assert result["success"] is False
    assert result["ip"] is None

def test_dns_with_monkeypatch(
    monkeypatch
):
    def fake_gethostbyname(domain):
        return "1.2.3.4"

    monkeypatch.setattr(
        network.socket,
        "gethostbyname",
        fake_gethostbyname
    )

    result = network.check_dns(
        "example.com"
    )

    assert result["ip"] == "1.2.3.4"

@patch("network.subprocess.run")
def test_get_default_gateway(
    mock_run
):
    mock_run.return_value.stdout = """
IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface
          0.0.0.0          0.0.0.0      192.168.1.1    192.168.1.20
"""

    gateway = get_default_gateway()

    assert gateway == "192.168.1.1"

@patch("network.subprocess.run")
def test_get_default_gateway_not_found(
    mock_run
):
    mock_run.return_value.stdout = """
IPv4 Route Table
No active default route.
"""

    gateway = get_default_gateway()

    assert gateway is None