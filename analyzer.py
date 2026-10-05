import re

def evaluate_wifi_signal(signal):
    if signal is None:
        return "无法获取信号强度"

    if signal >= 80:
        return "信号很好"

    elif signal >= 60:
        return "信号良好"

    elif signal >= 40:
        return "信号一般"

    elif signal >= 25:
        return "信号较弱"

    else:
        return "信号很弱"

def parse_ping_result(output):
    packet_loss = None
    minimum = None
    maximum = None
    average = None

    loss_match = re.search(
        r"\((\d+)% loss\)",
        output
    )

    if loss_match:
        packet_loss = int(
            loss_match.group(1)
        )

    time_match = re.search(
        r"Minimum = (\d+)ms, "
        r"Maximum = (\d+)ms, "
        r"Average = (\d+)ms",
        output
    )

    if time_match:
        minimum = int(
            time_match.group(1)
        )

        maximum = int(
            time_match.group(2)
        )

        average = int(
            time_match.group(3)
        )

    return {
        "packet_loss": packet_loss,
        "minimum": minimum,
        "maximum": maximum,
        "average": average
    }


def calculate_jitter(latencies):
    if len(latencies) < 2:
        return 0

    differences = []

    for i in range(
        1,
        len(latencies)
    ):
        difference = abs(
            latencies[i]
            - latencies[i - 1]
        )

        differences.append(
            difference
        )

    return (
        sum(differences)
        / len(differences)
    )


def evaluate_ping(
    packet_loss,
    average
):
    if packet_loss is None:
        return "无法判断"

    if packet_loss == 100:
        return "无法连接"

    if packet_loss > 10:
        return "网络很不稳定"

    if packet_loss > 0:
        return "存在丢包"

    if average is None:
        return "连接成功"

    if average < 30:
        return "网络很好"

    elif average < 80:
        return "网络正常"

    elif average < 150:
        return "延迟较高"

    return "网络延迟很高"


def evaluate_stability(
    packet_loss,
    average,
    maximum,
    jitter
):
    problems = []

    if packet_loss >= 10:
        problems.append(
            "存在严重丢包"
        )

    elif packet_loss > 0:
        problems.append(
            "存在少量丢包"
        )

    if average >= 150:
        problems.append(
            "平均延迟很高"
        )

    elif average >= 80:
        problems.append(
            "平均延迟偏高"
        )

    if maximum >= 500:
        problems.append(
            "出现瞬时超高延迟"
        )

    if jitter >= 50:
        problems.append(
            "网络抖动明显"
        )

    if not problems:
        problems.append(
            "网络整体比较稳定"
        )

    return problems