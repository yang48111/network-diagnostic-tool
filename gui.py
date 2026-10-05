import tkinter as tk
import threading
import math

from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from network import (
    get_wifi_info,
    run_ping,
    ping_once
)

from analyzer import (
    evaluate_wifi_signal,
    evaluate_ping,
    calculate_jitter,
    evaluate_stability
)

from diagnostic import (
    collect_diagnostic_data
)

chart_sequences = []
chart_latencies = []

def update_live_stats(
    completed,
    failed,
    latencies
):
    if completed > 0:
        packet_loss = (
            failed / completed
        ) * 100
    else:
        packet_loss = 0

    if latencies:
        average = (
            sum(latencies)
            / len(latencies)
        )

        maximum = max(
            latencies
        )
    else:
        average = None
        maximum = None

    def update():
        loss_var.set(
            f"Packet Loss: "
            f"{packet_loss:.1f}%"
        )

        if average is None:
            average_var.set(
                "Average: -"
            )
        else:
            average_var.set(
                f"Average: "
                f"{average:.1f} ms"
            )

        if maximum is None:
            max_latency_var.set(
                "Max latency: -"
            )
        else:
            max_latency_var.set(
                f"Max latency: "
                f"{maximum} ms"
            )

    root.after(
        0,
        update
    )

def reset_chart():
    chart_sequences.clear()
    chart_latencies.clear()

    line.set_data(
        [],
        []
    )

    axis.set_xlim(
        0,
        10
    )

    axis.set_ylim(
        0,
        100
    )

    canvas.draw_idle()

def update_chart(
    sequence,
    latency
):
    def update():
        chart_sequences.append(
            sequence
        )

        if latency is None:
            chart_latencies.append(
                float("nan")
            )
        else:
            chart_latencies.append(
                latency
            )

        line.set_data(
            chart_sequences,
            chart_latencies
        )

        update_chart_limits()

        canvas.draw_idle()

    root.after(
        0,
        update
    )

def update_chart_limits():
    if not chart_sequences:
        return

    max_sequence = max(
        chart_sequences
    )

    axis.set_xlim(
        0,
        max(10, max_sequence + 1)
    )

    valid_latencies = [
        value
        for value in chart_latencies
        if not math.isnan(value)
    ]

    if not valid_latencies:
        axis.set_ylim(
            0,
            100
        )
        return

    maximum = max(
        valid_latencies
    )

    upper_limit = max(
        100,
        maximum * 1.2
    )

    axis.set_ylim(
        0,
        upper_limit
    )

def cancel_stability_test():
    stop_event.set()

    status_var.set(
        "Cancelling..."
    )

def stability_worker(host, count):
    try:
        results = []
        latencies = []
        failed = 0
        cancelled = False

        safe_write_output(
            "========== Stability Test =========="
        )

        safe_write_output(
            f"Target: {host}"
        )

        safe_write_output(
            f"Requested: {count}"
        )

        safe_write_output("")

        for i in range(count):
            if stop_event.is_set():
                cancelled = True

                safe_write_output("")
                safe_write_output(
                    "Test cancelled by user."
                )
                break

            latency = ping_once(host)
            
            update_current_latency(
                latency
            )
            update_chart(
                i + 1,
                latency
            )

            if latency is None:
                failed += 1

                results.append({
                    "sequence": i + 1,
                    "latency": None,
                    "status": "timeout"
                })

                safe_write_output(
                    f"[{i + 1}/{count}] Timeout"
                )

            else:
                latencies.append(latency)

                results.append({
                    "sequence": i + 1,
                    "latency": latency,
                    "status": "success"
                })

                safe_write_output(
                    f"[{i + 1}/{count}] "
                    f"{latency} ms"
                )
                current_max = max(
                    latencies
                )

                root.after(
                    0,
                    lambda value=current_max:
                        max_latency_var.set(
                            f"Max latency: "
                            f"{value} ms"
                        )
                )

            update_progress(
                i + 1,
                count
            )

            completed = len(
                results
            )

            update_progress(
                completed,
                count
            )

            update_live_stats(
                completed,
                failed,
                latencies.copy()
            )



        completed = len(results)
        success = len(latencies)
        if completed > 0:
            packet_loss = (
                failed / completed
            ) * 100

        else:
            packet_loss = 0

        
        safe_write_output("")
        safe_write_output(
            "========== Statistics =========="
        )

        safe_write_output(
            f"Requested: {count}"
        )
        safe_write_output(
            f"Completed: {completed}"
        )
        safe_write_output(
            f"Success: {success}"
        )

        safe_write_output(
            f"Failed: {failed}"
        )

        safe_write_output(
            f"Packet Loss: "
            f"{packet_loss:.1f}%"
        )
        if cancelled:
            safe_write_output(
                "Status: Cancelled"
            )
        else:
            safe_write_output(
                "Status: Completed"
            )

        if not latencies:
            safe_write_output(
                "All ping attempts failed."
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

        safe_write_output(
            f"Minimum: {minimum} ms"
        )

        safe_write_output(
            f"Maximum: {maximum} ms"
        )

        safe_write_output(
            f"Average: {average:.1f} ms"
        )

        safe_write_output(
            f"Jitter: {jitter:.1f} ms"
        )

        problems = evaluate_stability(
            packet_loss,
            average,
            maximum,
            jitter
        )

        safe_write_output("")
        safe_write_output(
            "========== Result =========="
        )

        for problem in problems:
            safe_write_output(
                f"- {problem}"
            )

    except Exception as error:
        safe_write_output("")
        safe_write_output(
            f"Error: {error}"
        )

    finally:
        root.after(
            0,
            lambda: stability_button.config(
                state="normal"
            )
        )

        root.after(
            0,
            lambda: cancel_button.config(
                state="disabled"
            )
        )

        set_status(
            "Ready"
        )

def start_stability_test():

    latency_var.set(
        "Current latency: -"
    )

    average_var.set(
        "Average: -"
    )

    loss_var.set(
        "Packet Loss: -"
    )

    max_latency_var.set(
        "Max latency: -"
    )
    
    
    host = host_entry.get().strip()

    if not host:
        host = "8.8.8.8"

    count_text = (
        count_entry.get().strip()
    )
    try:
        count = int(count_text)
        

    except ValueError:
        clear_output()

        write_output(
            "Count must be a number."
        )

        return

    if count < 1:
        clear_output()
        write_output(
            "Count must be at least 1."
        )
        return
    if count > 1000:
        clear_output()
        write_output(
            "Count cannot exceed 1000."
        )
        return
    
    clear_output()

    reset_chart()

    stop_event.clear()

    progress_bar["maximum"] = count
    progress_bar["value"] = 0

    progress_label.config(
        text=f"0 / {count}"
    )

    latency_var.set(
        "Current latency: -"
    )

    max_latency_var.set(
        "Max latency: -"
    )

    stability_button.config(
        state="disabled"
    )
    cancel_button.config(
        state="normal"
    )

    status_var.set(
        "Running stability test..."
    )

    thread = threading.Thread(
        target=stability_worker,
        args=(host, count),
        daemon=True
    )

    thread.start()

    



def clear_output():
    output_text.delete(
        "1.0",
        tk.END
    )


def write_output(text):
    output_text.insert(
        tk.END,
        text + "\n"
    )

    output_text.see(
        tk.END
    )

def safe_write_output(text=""):
    root.after(
        0,
        lambda: write_output(text)
    )

def show_wifi():
    clear_output()

    write_output(
        "========== Wi-Fi Information =========="
    )

    wifi = get_wifi_info()

    if not wifi["ssid"]:
        write_output(
            "No connected Wi-Fi detected."
        )

        write_output(
            "The computer may be using Ethernet."
        )

        return

    write_output(
        f"SSID: {wifi['ssid']}"
    )

    write_output(
        f"BSSID: {wifi['bssid']}"
    )

    write_output(
        f"State: {wifi['state']}"
    )

    write_output(
        f"Radio Type: {wifi['radio_type']}"
    )

    write_output(
        f"Band: {wifi['band']}"
    )

    write_output(
        f"Channel: {wifi['channel']}"
    )

    write_output(
        f"Receive Rate: "
        f"{wifi['receive_rate']} Mbps"
    )

    write_output(
        f"Transmit Rate: "
        f"{wifi['transmit_rate']} Mbps"
    )

    if wifi["signal"] is not None:
        write_output(
            f"Signal: {wifi['signal']}%"
        )

    rating = evaluate_wifi_signal(
        wifi["signal"]
    )

    write_output(
        f"Signal Rating: {rating}"
    )

def ping_worker(host):
    try:
        safe_write_output(
            f"Ping target: {host}"
        )

        safe_write_output(
            "Testing..."
        )

        data = run_ping(host)

        safe_write_output("")

        if data["packet_loss"] is not None:
            safe_write_output(
                f"Packet Loss: "
                f"{data['packet_loss']}%"
            )

        if data["minimum"] is not None:
            safe_write_output(
                f"Minimum: "
                f"{data['minimum']} ms"
            )

        if data["maximum"] is not None:
            safe_write_output(
                f"Maximum: "
                f"{data['maximum']} ms"
            )

        if data["average"] is not None:
            safe_write_output(
                f"Average: "
                f"{data['average']} ms"
            )

        status = evaluate_ping(
            data["packet_loss"],
            data["average"]
        )

        safe_write_output("")
        safe_write_output(
            f"Result: {status}"
        )

    except Exception as error:
        safe_write_output(
            f"Error: {error}"
        )

def start_ping(host):
    clear_output()

    thread = threading.Thread(
        target=ping_worker,
        args=(host,),
        daemon=True
    )

    thread.start()

def update_current_latency(
    latency
):
    if latency is None:
        text = (
            "Current latency: Timeout"
        )

    else:
        text = (
            f"Current latency: "
            f"{latency} ms"
        )

    root.after(
        0,
        lambda: latency_var.set(
            text
        )
    )

def show_ping(host):
    clear_output()

    write_output(
        f"Ping target: {host}"
    )

    write_output(
        "Testing..."
    )

    data = run_ping(host)

    write_output()

    if data["packet_loss"] is not None:
        write_output(
            f"Packet Loss: "
            f"{data['packet_loss']}%"
        )

    if data["minimum"] is not None:
        write_output(
            f"Minimum: "
            f"{data['minimum']} ms"
        )

    if data["maximum"] is not None:
        write_output(
            f"Maximum: "
            f"{data['maximum']} ms"
        )

    if data["average"] is not None:
        write_output(
            f"Average: "
            f"{data['average']} ms"
        )

    status = evaluate_ping(
        data["packet_loss"],
        data["average"]
    )

    write_output()

    write_output(
        f"Result: {status}"
    )

def custom_ping():
    host = host_entry.get().strip()

    if not host:
        clear_output()

        write_output(
            "Please enter an IP address or domain."
        )

        return

    start_ping(host)

def show_full_diagnostic():
    clear_output()

    write_output(
        "========== Network Diagnostic =========="
    )

    write_output(
        "Running diagnostic..."
    )

    write_output("")

    data = collect_diagnostic_data()

    wifi = data["wifi"]

    write_output("[Wi-Fi]")

    if wifi and wifi["ssid"]:
        write_output(
            f"SSID: {wifi['ssid']}"
        )

        if wifi["signal"] is not None:
            write_output(
                f"Signal: {wifi['signal']}%"
            )
    else:
        write_output(
            "No connected Wi-Fi detected."
        )

    write_output("")

    write_output("[Gateway]")

    if data["gateway"]:
        write_output(
            f"Gateway: {data['gateway']}"
        )
    else:
        write_output(
            "Gateway: Not found"
        )

    if data["gateway_test"]:
        gateway_test = (
            data["gateway_test"]
        )

        write_output(
            f"Packet Loss: "
            f"{gateway_test['packet_loss']}%"
        )

        write_output(
            f"Average: "
            f"{gateway_test['average']} ms"
        )

    write_output("")

    write_output("[Internet]")

    if data["internet"]:
        internet = data["internet"]

        write_output(
            f"Packet Loss: "
            f"{internet['packet_loss']}%"
        )

        write_output(
            f"Average: "
            f"{internet['average']} ms"
        )
    else:
        write_output(
            "Internet test unavailable."
        )

    write_output("")

    write_output("[DNS]")

    if data["dns"]:
        dns = data["dns"]

        if dns["success"]:
            write_output(
                f"{dns['domain']} -> "
                f"{dns['ip']}"
            )
        else:
            write_output(
                "DNS resolution failed."
            )
    else:
        write_output(
            "DNS test unavailable."
        )

    write_output("")
    write_output(
        "========== Conclusion =========="
    )

    write_output(
        data["conclusion"]
    )

def full_diagnostic_worker():
    try:
        safe_write_output(
            "========== Network Diagnostic =========="
        )

        safe_write_output(
            "Running diagnostic..."
        )

        data = collect_diagnostic_data()

        safe_write_output("")
        safe_write_output("[Wi-Fi]")

        wifi = data["wifi"]

        if wifi and wifi["ssid"]:
            safe_write_output(
                f"SSID: {wifi['ssid']}"
            )

            if wifi["signal"] is not None:
                safe_write_output(
                    f"Signal: {wifi['signal']}%"
                )

        else:
            safe_write_output(
                "No connected Wi-Fi detected."
            )

        safe_write_output("")
        safe_write_output("[Gateway]")

        if data["gateway"]:
            safe_write_output(
                f"Gateway: {data['gateway']}"
            )

        if data["gateway_test"]:
            gateway = (
                data["gateway_test"]
            )

            safe_write_output(
                f"Packet Loss: "
                f"{gateway['packet_loss']}%"
            )

            safe_write_output(
                f"Average: "
                f"{gateway['average']} ms"
            )

        safe_write_output("")
        safe_write_output("[Internet]")

        if data["internet"]:
            internet = data["internet"]

            safe_write_output(
                f"Packet Loss: "
                f"{internet['packet_loss']}%"
            )

            safe_write_output(
                f"Average: "
                f"{internet['average']} ms"
            )

        safe_write_output("")
        safe_write_output("[DNS]")

        if data["dns"]:
            dns = data["dns"]

            if dns["success"]:
                safe_write_output(
                    f"{dns['domain']} -> "
                    f"{dns['ip']}"
                )

            else:
                safe_write_output(
                    "DNS resolution failed."
                )

        safe_write_output("")
        safe_write_output(
            "========== Conclusion =========="
        )

        safe_write_output(
            data["conclusion"]
        )

    except Exception as error:
        safe_write_output(
            f"Error: {error}"
        )

    finally:
        root.after(
            0,
            lambda: diagnostic_button.config(
                state="normal"
            )
        )

stop_event = threading.Event()
root = tk.Tk()

root.title(
    "Network Diagnostic Tool"
)

root.geometry(
    "1000x800"
)

root.minsize(
    850,
    700
)

title_label = ttk.Label(
    root,
    text="Network Diagnostic Tool",
    font=(
        "Segoe UI",
        20,
        "bold"
    )
)

title_label.pack(
    pady=15
)

button_frame = ttk.Frame(
    root
)

button_frame.pack(
    pady=10
)

stability_button = ttk.Button(
    button_frame,
    text="Stability Test",
    command=start_stability_test
)

stability_button.pack(
    side="left",
    padx=5
)

wifi_button = ttk.Button(
    button_frame,
    text="Wi-Fi Information",
    command=show_wifi
)

wifi_button.pack(
    side="left",
    padx=5
)

google_button = ttk.Button(
    button_frame,
    text="Ping Google",
    command=lambda: start_ping(
        "google.com"
    )
)

google_button.pack(
    side="left",
    padx=5
)

internet_button = ttk.Button(
    button_frame,
    text="Ping 8.8.8.8",
    command=lambda: start_ping(
        "8.8.8.8"
    )
)

internet_button.pack(
    side="left",
    padx=5
)

diagnostic_button = ttk.Button(
    button_frame,
    text="Full Diagnostic",
    command=show_full_diagnostic
)

def start_full_diagnostic():
    clear_output()

    diagnostic_button.config(
        state="disabled"
    )

    thread = threading.Thread(
        target=full_diagnostic_worker,
        daemon=True
    )

    thread.start()

def update_progress(current, total):
    def update():
        progress_bar["maximum"] = total
        progress_bar["value"] = current

        progress_label.config(
            text=f"{current} / {total}"
        )

    root.after(
        0,
        update
    )

diagnostic_button.pack(
    side="left",
    padx=5
)





average_var = tk.StringVar(
    value="Average: -"
)

loss_var = tk.StringVar(
    value="Packet Loss: -"
)

stats_frame = ttk.Frame(
    root
)

stats_frame.pack(
    pady=5
)



average_label = ttk.Label(
    stats_frame,
    textvariable=average_var
)

average_label.pack(
    side="left",
    padx=15
)

loss_label = ttk.Label(
    stats_frame,
    textvariable=loss_var
)

loss_label.pack(
    side="left",
    padx=15
)

ping_frame = ttk.Frame(
    root
)

ping_frame.pack(
    pady=10
)

host_label = ttk.Label(
    ping_frame,
    text="Host:"
)

host_label.pack(
    side="left"
)

host_entry = ttk.Entry(
    ping_frame,
    width=35
)

host_entry.pack(
    side="left",
    padx=8
)

host_entry.insert(
    0,
    "8.8.8.8"
)

chart_frame = ttk.Frame(
    root
)

chart_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

custom_ping_button = ttk.Button(
    ping_frame,
    text="Ping",
    command=custom_ping
)

custom_ping_button.pack(
    side="left"
)

cancel_button = ttk.Button(
    button_frame,
    text="Cancel",
    command=cancel_stability_test,
    state="disabled"
)

cancel_button.pack(
    side="left",
    padx=5
)

progress_frame = ttk.Frame(
    root
)

progress_frame.pack(
    fill="x",
    padx=20,
    pady=5
)

progress_bar = ttk.Progressbar(
    progress_frame,
    orient="horizontal",
    mode="determinate",
    maximum=30
)

progress_bar.pack(
    side="left",
    fill="x",
    expand=True
)

progress_label = ttk.Label(
    progress_frame,
    text="0 / 30"
)

progress_label.pack(
    side="left",
    padx=10
)

output_text = ScrolledText(
    root,
    width=90,
    height=25,
    font=(
        "Consolas",
        10
    )
)

output_text.pack(
    padx=20,
    pady=15,
    fill="both",
    expand=True
)

count_label = ttk.Label(
    ping_frame,
    text="Count:"
)

count_label.pack(
    side="left",
    padx=(15, 0)
)

count_entry = ttk.Entry(
    ping_frame,
    width=6
)

count_entry.pack(
    side="left",
    padx=5
)

count_entry.insert(
    0,
    "30"
)

latency_var = tk.StringVar(
    value="Current latency: -"
)
latency_label = ttk.Label(
    root,
    textvariable=latency_var
)

latency_label.pack(
    pady=3
)

current_label = ttk.Label(
    stats_frame,
    textvariable=latency_var
)

current_label.pack(
    side="left",
    padx=15
)

max_latency_var = tk.StringVar(
    value="Max latency: -"
)
max_latency_label = ttk.Label(
    root,
    textvariable=max_latency_var
)

max_label = ttk.Label(
    stats_frame,
    textvariable=max_latency_var
)

max_label.pack(
    side="left",
    padx=15
)

max_latency_label.pack(
    pady=3
)

write_output(
    "Network Diagnostic Tool ready."
)

write_output(
    "Select a function above."
)

status_var = tk.StringVar(
    value="Ready"
)
status_label = ttk.Label(
    root,
    textvariable=status_var
)

status_label.pack(
    pady=5
)



figure = Figure(
    figsize=(7, 3),
    dpi=100
)

axis = figure.add_subplot(111)
axis.set_title(
    "Network Latency"
)

axis.set_xlabel(
    "Ping Sequence"
)

axis.set_ylabel(
    "Latency (ms)"
)

axis.grid(True)
line, = axis.plot(
    [],
    [],
    marker="o"
)
canvas = FigureCanvasTkAgg(
    figure,
    master=chart_frame
)

canvas.draw()

canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)

def set_status(text):
    root.after(
        0,
        lambda: status_var.set(text)
    )

root.mainloop()