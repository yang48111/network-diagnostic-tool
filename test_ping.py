import subprocess


result = subprocess.run(
    ["ping", "google.com"],
    capture_output=True,
    text=True
)

print(result)