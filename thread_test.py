import threading
import time


def work():
    for i in range(5):
        print("Working:", i)
        time.sleep(1)


thread = threading.Thread(
    target=work
)

thread.start()

print("Main thread continues...")