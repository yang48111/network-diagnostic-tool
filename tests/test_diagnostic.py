from unittest.mock import patch

from diagnostic import (
    collect_diagnostic_data
)


@patch("diagnostic.check_dns")
@patch("diagnostic.run_ping")
@patch("diagnostic.get_default_gateway")
@patch("diagnostic.get_wifi_info")
def test_full_diagnostic_success(
    mock_wifi,
    mock_gateway,
    mock_ping,
    mock_dns
):
    mock_wifi.return_value = {
        "ssid": "TestWiFi",
        "signal": 90
    }

    mock_gateway.return_value = (
        "192.168.1.1"
    )

    mock_ping.return_value = {
        "success": True,
        "packet_loss": 0,
        "minimum": 1,
        "maximum": 20,
        "average": 10
    }

    mock_dns.return_value = {
        "success": True,
        "domain": "google.com",
        "ip": "1.2.3.4"
    }

    result = (
        collect_diagnostic_data()
    )

    assert (
        result["conclusion"]
        == "网络连接基本正常"
    )

@patch("diagnostic.get_wifi_info")
@patch("diagnostic.get_default_gateway")
@patch("diagnostic.run_ping")
def test_gateway_failure(
    mock_ping,
    mock_gateway,
    mock_wifi
):
    mock_wifi.return_value = {
        "ssid": "TestWiFi",
        "signal": 80
    }

    mock_gateway.return_value = (
        "192.168.1.1"
    )

    mock_ping.return_value = {
        "success": False,
        "packet_loss": 100,
        "average": None
    }

    result = (
        collect_diagnostic_data()
    )

    assert (
        "默认网关"
        in result["conclusion"]
    )