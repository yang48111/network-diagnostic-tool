from pathlib import Path
from datetime import datetime

from paths import get_reports_dir

def generate_report(data):
    content = build_report(data)

    file_path = save_report(
        content
    )

    return file_path

def build_report(data):
    lines = []

    lines.append(
        "=" * 60
    )
    lines.append(
        "Network Diagnostic Report"
    )
    lines.append(
        "=" * 60
    )
    lines.append("")

    report_time = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    lines.append(
        f"Time: {report_time}"
    )

    lines.append("")

    # Wi-Fi
    lines.append("[Wi-Fi]")

    wifi = data["wifi"]

    if wifi and wifi["ssid"]:
        lines.append(
            f"SSID: {wifi['ssid']}"
        )

        lines.append(
            f"BSSID: {wifi['bssid']}"
        )

        lines.append(
            f"Signal: {wifi['signal']}%"
        )

        lines.append(
            f"Band: {wifi['band']}"
        )

        lines.append(
            f"Channel: {wifi['channel']}"
        )

        lines.append(
            f"Receive Rate: "
            f"{wifi['receive_rate']} Mbps"
        )

        lines.append(
            f"Transmit Rate: "
            f"{wifi['transmit_rate']} Mbps"
        )

    else:
        lines.append(
            "No connected Wi-Fi detected"
        )

    lines.append("")

    # Gateway
    lines.append("[Gateway]")

    lines.append(
        f"Address: {data['gateway']}"
    )

    gateway_test = (
        data["gateway_test"]
    )

    if gateway_test:
        lines.append(
            f"Packet Loss: "
            f"{gateway_test['packet_loss']}%"
        )

        lines.append(
            f"Average Latency: "
            f"{gateway_test['average']} ms"
        )

    lines.append("")

    # Internet
    lines.append("[Internet]")

    internet = data["internet"]

    if internet:
        lines.append(
            "Target: 8.8.8.8"
        )

        lines.append(
            f"Packet Loss: "
            f"{internet['packet_loss']}%"
        )

        lines.append(
            f"Average Latency: "
            f"{internet['average']} ms"
        )

    else:
        lines.append(
            "Internet test unavailable"
        )

    lines.append("")

    # DNS
    lines.append("[DNS]")

    dns = data["dns"]

    if dns:
        if dns["success"]:
            lines.append(
                f"{dns['domain']} -> "
                f"{dns['ip']}"
            )

        else:
            lines.append(
                "DNS resolution failed"
            )

    else:
        lines.append(
            "DNS test unavailable"
        )

    lines.append("")

    # Conclusion
    lines.append("[Conclusion]")

    lines.append(
        data["conclusion"]
    )

    lines.append("")
    lines.append(
        "=" * 60
    )

    return "\n".join(lines)

def save_report(content):
    try:
        report_dir = (
            get_reports_dir()
        )


        filename_time = (
            datetime.now().strftime(
                "%Y-%m-%d_%H%M%S"
            )
        )

        filename = (
            f"network_report_"
            f"{filename_time}.txt"
        )

        file_path = (
            report_dir / filename
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(content)

        return file_path

    except OSError as error:
        print(
            f"保存报告失败: {error}"
        )

        return None