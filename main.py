from network import get_network_info

from diagnostic import (
    show_ping_result,
    run_full_diagnostic,
    stability_test,
    show_wifi_info,
    collect_diagnostic_data
)

from report import generate_report

def show_menu():
    print()
    print("=" * 50)
    print("        Network Diagnostic Tool")
    print("=" * 50)

    print("1. 查看本机网络信息")
    print("2. 查看 Wi-Fi 信息")
    print("3. Ping Google")
    print("4. Ping 8.8.8.8")
    print("5. 自定义 Ping")
    print("6. 网络综合检测")
    print("7. 网络稳定性测试")
    print("8. 保存网络诊断报告")
    print("0. 退出")

    print("=" * 50)


def main():
    while True:
        show_menu()

        choice = input(
            "请选择功能: "
        ).strip()

        if choice == "1":
            get_network_info()

        elif choice == "2":
            show_wifi_info()

        elif choice == "3":
            show_ping_result(
                "google.com"
            )

        elif choice == "4":
            show_ping_result(
                "8.8.8.8"
            )

        elif choice == "5":
            host = input(
                "请输入 IP 或域名: "
            ).strip()

            if host:
                show_ping_result(host)

        elif choice == "6":
            run_full_diagnostic()

        elif choice == "7":
            host = input(
                "测试目标 "
                "[默认 8.8.8.8]: "
            ).strip()

            if not host:
                host = "8.8.8.8"

            stability_test(host)

        elif choice == "8":
            print(
                "正在收集诊断数据..."
            )

            data = collect_diagnostic_data()

            file_path = generate_report(
                data
            )

            if file_path:
                print(
                    f"报告已保存: {file_path}"
                )
            else:
                print(
                    "报告保存失败"
                )

        elif choice == "0":
            print("程序已退出")
            break

        else:
            print(
                "无效选项"
            )


if __name__ == "__main__":
    main()