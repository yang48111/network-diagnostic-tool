import csv
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime
from paths import get_reports_dir

def save_ping_chart(
    host,
    results
):
    report_dir = (
        get_reports_dir()
    )

    timestamp = (
        datetime.now().strftime(
            "%Y-%m-%d_%H%M%S"
        )
    )

    filename = (
        f"ping_{timestamp}.png"
    )

    file_path = (
        report_dir / filename
    )

    x_values = []

    y_values = []

    for item in results:
        x_values.append(
            item["sequence"]
        )

        if item["latency"] is None:
            y_values.append(
                float("nan")
            )
        else:
            y_values.append(
                item["latency"]
            )

    if all(
        item["latency"] is None
        for item in results
    ):
        return None

    plt.figure()

    plt.plot(
        x_values,
        y_values,
        marker="o"
    )

    plt.xlabel(
        "Ping Sequence"
    )

    plt.ylabel(
        "Latency (ms)"
    )

    plt.title(
        f"Network Latency - {host}"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        file_path
    )

    plt.close()

    return file_path

def save_ping_csv(host, results):
    report_dir = (
        get_reports_dir()
    )

    timestamp = (
        datetime.now().strftime(
            "%Y-%m-%d_%H%M%S"
        )
    )

    filename = (
        f"ping_{timestamp}.csv"
    )

    file_path = (
        report_dir / filename
    )

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "sequence",
                "host",
                "latency_ms",
                "status"
            ]
        )

        for item in results:
            writer.writerow(
                [
                    item["sequence"],
                    host,
                    item["latency"],
                    item["status"]
                ]
            )

    return file_path