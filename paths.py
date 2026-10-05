import sys
from pathlib import Path


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(
            sys.executable
        ).resolve().parent

    return Path(
        __file__
    ).resolve().parent


def get_reports_dir():
    report_dir = (
        get_app_dir()
        / "reports"
    )

    report_dir.mkdir(
        exist_ok=True
    )

    return report_dir