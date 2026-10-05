from datetime import datetime

from paths import get_app_dir


def log_error(error):
    log_path = (
        get_app_dir()
        / "error.log"
    )

    with open(
        log_path,
        "a",
        encoding="utf-8"
    ) as file:
        time_text = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        file.write(
            f"[{time_text}] "
            f"{error}\n"
        )