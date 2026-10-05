from analyzer import (
    calculate_jitter,
    evaluate_ping,
    parse_ping_result
)

def test_calculate_jitter():
    latencies = [
        10,
        20,
        30
    ]

    result = calculate_jitter(
        latencies
    )

    assert result == 10

def test_calculate_jitter_with_one_value():
    result = calculate_jitter(
        [20]
    )

    assert result == 0


def test_calculate_jitter_with_empty_list():
    result = calculate_jitter(
        []
    )

    assert result == 0

def test_evaluate_ping_good():
    result = evaluate_ping(
        packet_loss=0,
        average=20
    )

    assert result == "网络很好"


def test_evaluate_ping_normal():
    result = evaluate_ping(
        packet_loss=0,
        average=50
    )

    assert result == "网络正常"


def test_evaluate_ping_high_latency():
    result = evaluate_ping(
        packet_loss=0,
        average=120
    )

    assert result == "延迟较高"


def test_evaluate_ping_unreachable():
    result = evaluate_ping(
        packet_loss=100,
        average=None
    )

    assert result == "无法连接"

def test_evaluate_ping_packet_loss():
    result = evaluate_ping(
        packet_loss=5,
        average=20
    )

    assert result == "存在丢包"


def test_evaluate_ping_serious_packet_loss():
    result = evaluate_ping(
        packet_loss=25,
        average=20
    )

    assert result == "网络很不稳定"

def test_parse_ping_result():
    output = """
Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),

Minimum = 12ms, Maximum = 30ms, Average = 18ms
"""

    result = parse_ping_result(
        output
    )

    assert result["packet_loss"] == 0
    assert result["minimum"] == 12
    assert result["maximum"] == 30
    assert result["average"] == 18

def test_parse_ping_result_with_loss():
    output = """
Packets: Sent = 4, Received = 3, Lost = 1 (25% loss),

Minimum = 15ms, Maximum = 40ms, Average = 22ms
"""

    result = parse_ping_result(
        output
    )

    assert result["packet_loss"] == 25
    assert result["minimum"] == 15
    assert result["maximum"] == 40
    assert result["average"] == 22