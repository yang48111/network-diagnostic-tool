from exporter import (
    save_ping_csv,
    save_ping_chart
)

from network import (
    run_ping,
    ping_once,
    get_default_gateway,
    check_dns,
    get_wifi_info
)

from analyzer import (
    calculate_jitter,
    evaluate_ping,
    evaluate_stability,
    evaluate_wifi_signal
)

def collect_stability_data(host, count=30):
    results = []

    for i in range(count):
        latency = ping_once(host)

        if latency is None:
            result = {
                "sequence": i + 1,
                "latency": None,
                "status": "timeout"
            }

        else:
            result = {
                "sequence": i + 1,
                "latency": latency,
                "status": "success"
            }

        results.append(result)

    return results

def show_full_diagnostic():
    print()
    print("=" * 50)
    print("              网络综合诊断")
    print("=" * 50)

    data = collect_diagnostic_data()

    wifi = data["wifi"]

    print("\n[Wi-Fi]")

    if wifi and wifi["ssid"]:
        print(
            f"SSID: {wifi['ssid']}"
        )

        if wifi["signal"] is not None:
            print(
                f"Signal: "
                f"{wifi['signal']}%"
            )
    else:
        print(
            "未检测到 Wi-Fi，"
            "可能正在使用 Ethernet"
        )

    print("\n[Gateway]")

    if data["gateway"]:
        print(
            f"Gateway: "
            f"{data['gateway']}"
        )

    gateway_test = (
        data["gateway_test"]
    )

    if gateway_test:
        print(
            f"Packet Loss: "
            f"{gateway_test['packet_loss']}%"
        )

        print(
            f"Average: "
            f"{gateway_test['average']} ms"
        )

    print("\n[Internet]")

    internet = data["internet"]

    if internet:
        print(
            f"8.8.8.8 Packet Loss: "
            f"{internet['packet_loss']}%"
        )

        print(
            f"Average: "
            f"{internet['average']} ms"
        )

    print("\n[DNS]")

    dns = data["dns"]

    if dns:
        if dns["success"]:
            print(
                f"{dns['domain']} -> "
                f"{dns['ip']}"
            )
        else:
            print(
                "DNS resolution failed"
            )

    print()
    print("=" * 50)
    print(
        f"诊断结论："
        f"{data['conclusion']}"
    )
    print("=" * 50)

    return data

def collect_diagnostic_data():
    data = {
        "wifi": None,
        "gateway": None,
        "gateway_test": None,
        "internet": None,
        "dns": None,
        "conclusion": None
    }

    wifi = get_wifi_info()

    data["wifi"] = wifi

    gateway = get_default_gateway()

    data["gateway"] = gateway

    if gateway is None:
        data["conclusion"] = (
            "无法找到默认网关，"
            "请检查网络连接"
        )

        return data

    gateway_result = run_ping(
        gateway
    )

    data["gateway_test"] = (
        gateway_result
    )

    if not gateway_result["success"]:
        data["conclusion"] = (
            "无法连接默认网关，"
            "可能存在 Wi-Fi、"
            "网卡或路由器问题"
        )

        return data

    internet_result = run_ping(
        "8.8.8.8"
    )

    data["internet"] = (
        internet_result
    )

    if not internet_result["success"]:
        data["conclusion"] = (
            "局域网正常，"
            "但 Internet 连接异常"
        )

        return data

    dns_result = check_dns(
        "google.com"
    )

    data["dns"] = dns_result

    if not dns_result["success"]:
        data["conclusion"] = (
            "Internet 可以访问，"
            "但 DNS 解析异常"
        )

        return data

    data["conclusion"] = (
        "网络连接基本正常"
    )

    return data

def show_wifi_info():
    print()
    print("=" * 50)
    print("              Wi-Fi 信息")
    print("=" * 50)

    wifi = get_wifi_info()

    if not wifi["ssid"]:
        print("当前没有检测到已连接的 Wi-Fi")
        return

    print(
        f"SSID: {wifi['ssid']}"
    )

    print(
        f"BSSID: {wifi['bssid']}"
    )

    print(
        f"状态: {wifi['state']}"
    )

    print(
        f"无线标准: "
        f"{wifi['radio_type']}"
    )

    print(
        f"频段: {wifi['band']}"
    )

    print(
        f"信道: {wifi['channel']}"
    )

    print(
        f"接收速率: "
        f"{wifi['receive_rate']} Mbps"
    )

    print(
        f"发送速率: "
        f"{wifi['transmit_rate']} Mbps"
    )

    print(
        f"信号强度: "
        f"{wifi['signal']}%"
    )

    rating = evaluate_wifi_signal(
        wifi["signal"]
    )

    print(
        f"信号评价: {rating}"
    )

    return wifi

def show_ping_result(host):
    data = run_ping(host)

    print()
    print("=" * 50)
    print("              Ping 测试")
    print("=" * 50)

    print(f"目标: {host}")

    if data["packet_loss"] is not None:
        print(
            f"丢包率: "
            f"{data['packet_loss']}%"
        )

    if data["average"] is not None:
        print(
            f"最低延迟: "
            f"{data['minimum']} ms"
        )

        print(
            f"最高延迟: "
            f"{data['maximum']} ms"
        )

        print(
            f"平均延迟: "
            f"{data['average']} ms"
        )

    status = evaluate_ping(
        data["packet_loss"],
        data["average"]
    )

    print(
        f"诊断结果: {status}"
    )

    return data

def run_full_diagnostic():
    print()
    print("=" * 50)
    print("              网络综合诊断")
    print("=" * 50)

    print("\n[1/5] 检测 Wi-Fi...")

    wifi = get_wifi_info()

    if wifi["ssid"]:
        print(
            f"[OK] 已连接 Wi-Fi: "
            f"{wifi['ssid']}"
        )

        if wifi["signal"] is not None:
            print(
                f"信号强度: "
                f"{wifi['signal']}%"
            )

    else:
        print(
            "[INFO] 未检测到 Wi-Fi，"
            "可能正在使用 Ethernet"
        )

    print("\n[2/5] 获取默认网关")

    gateway = get_default_gateway()

    if gateway is None:
        print(
            "[FAIL] 无法找到默认网关"
        )
        return

    print(
        f"[OK] 默认网关: "
        f"{gateway}"
    )

    print(
        "\n[3/5] 测试局域网"
    )

    gateway_result = run_ping(
        gateway
    )

    if not gateway_result["success"]:
        print(
            "[FAIL] 默认网关无法访问"
        )
        print(
            "可能是 Wi-Fi、网卡"
            "或路由器问题"
        )
        return

    print(
        "[OK] 默认网关连接正常"
    )

    print(
        "\n[4/5] 测试 Internet"
    )

    internet_result = run_ping(
        "8.8.8.8"
    )

    if not internet_result["success"]:
        print(
            "[FAIL] Internet "
            "连接异常"
        )
        return

    print(
        "[OK] Internet 连接正常"
    )

    print(
        "\n[5/5] 测试 DNS"
    )

    dns_result = check_dns(
        "google.com"
    )

    if not dns_result["success"]:
        print(
            "[FAIL] DNS 解析失败"
        )
        return

    print(
        f"[OK] google.com -> "
        f"{dns_result['ip']}"
    )

    print()
    print("=" * 50)
    print(
        "诊断结果：网络基本正常"
    )
    print("=" * 50)

def stability_test(host, count=30):
    print()
    print("=" * 50)
    print("           网络稳定性测试")
    print("=" * 50)
    print(f"目标: {host}")
    print(f"测试次数: {count}")
    print()

    results = []

    for i in range(count):
        latency = ping_once(host)

        if latency is None:
            print(
                f"[{i + 1}/{count}] "
                f"Timeout"
            )

            results.append(
                {
                    "sequence": i + 1,
                    "latency": None,
                    "status": "timeout"
                }
            )

        else:
            print(
                f"[{i + 1}/{count}] "
                f"{latency} ms"
            )

            results.append(
                {
                    "sequence": i + 1,
                    "latency": latency,
                    "status": "success"
                }
            )

    latencies = [
        item["latency"]
        for item in results
        if item["latency"]
        is not None
    ]

    failed = (
        count - len(latencies)
    )

    packet_loss = (
        failed / count
    ) * 100

    print()
    print("=" * 50)
    print("              测试统计")
    print("=" * 50)

    print(f"测试次数: {count}")
    print(
        f"成功次数: "
        f"{len(latencies)}"
    )
    print(f"失败次数: {failed}")

    print(
        f"丢包率: "
        f"{packet_loss:.1f}%"
    )

    if not latencies:
        print("所有测试均失败")

        csv_path = save_ping_csv(
            host,
            results
        )

        print(
            f"CSV 已保存: "
            f"{csv_path}"
        )

        return

    minimum = min(latencies)
    maximum = max(latencies)

    average = (
        sum(latencies)
        / len(latencies)
    )

    jitter = calculate_jitter(
        latencies
    )

    print(
        f"最低延迟: "
        f"{minimum} ms"
    )

    print(
        f"最高延迟: "
        f"{maximum} ms"
    )

    print(
        f"平均延迟: "
        f"{average:.1f} ms"
    )

    print(
        f"平均抖动: "
        f"{jitter:.1f} ms"
    )

    problems = evaluate_stability(
        packet_loss,
        average,
        maximum,
        jitter
    )

    print()
    print("诊断结果:")

    for problem in problems:
        print(
            f"- {problem}"
        )

    csv_path = save_ping_csv(
        host,
        results
    )

    chart_path = save_ping_chart(
        host,
        results
    )

    print()
    print(
        f"CSV 已保存: "
        f"{csv_path}"
    )

    if chart_path:
        print(
            f"延迟图已保存: "
            f"{chart_path}"
        )

    return results